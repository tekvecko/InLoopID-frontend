from __future__ import annotations

import base64
import hashlib
import os
import re
import subprocess
import tempfile
from pathlib import Path

import requests


BACKEND_DIR = Path(__file__).resolve().parent

DEFAULT_TSA_URL = "https://freetsa.org/tsr"
DEFAULT_CA_FILE = BACKEND_DIR / "cacert.pem"

_SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


class TSAError(RuntimeError):
    pass


def validate_sha256_digest(value: str) -> str:
    if not isinstance(value, str):
        raise TSAError("SHA-256 digest must be a string")

    value = value.strip().lower()

    if not _SHA256_RE.fullmatch(value):
        raise TSAError(
            "content_hash must be exactly 64 hexadecimal characters"
        )

    return value


def tsa_url() -> str:
    value = os.getenv(
        "TSA_SERVER_URL",
        DEFAULT_TSA_URL,
    ).strip()

    if not value.startswith("https://"):
        raise TSAError(
            "TSA_SERVER_URL must use HTTPS"
        )

    return value


def ca_file() -> Path:
    path = Path(
        os.getenv(
            "TSA_CA_FILE",
            str(DEFAULT_CA_FILE),
        )
    ).expanduser().resolve()

    if not path.is_file():
        raise TSAError(
            f"TSA CA file does not exist: {path}"
        )

    return path


def _run(
    args: list[str],
) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            args,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
        )
    except subprocess.CalledProcessError as exc:
        stdout = (
            exc.stdout.decode(
                "utf-8",
                errors="replace",
            )
            if exc.stdout
            else ""
        )

        stderr = (
            exc.stderr.decode(
                "utf-8",
                errors="replace",
            )
            if exc.stderr
            else ""
        )

        raise TSAError(
            "OpenSSL TSA operation failed: "
            f"stdout={stdout!r} stderr={stderr!r}"
        ) from exc


def verify_tsr_bytes(
    content_hash_hex: str,
    tsr_bytes: bytes,
) -> tuple[bool, str]:
    digest = validate_sha256_digest(
        content_hash_hex
    )

    if not tsr_bytes:
        return False, "Empty TSA response"

    path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".tsr",
        ) as handle:
            handle.write(tsr_bytes)
            path = handle.name

        command = [
            "openssl",
            "ts",
            "-verify",
            "-in",
            path,
            "-digest",
            digest,
            "-CAfile",
            str(ca_file()),
        ]

        untrusted = os.getenv(
            "TSA_UNTRUSTED_FILE"
        )

        if untrusted:
            untrusted_path = (
                Path(untrusted)
                .expanduser()
                .resolve()
            )

            if not untrusted_path.is_file():
                return (
                    False,
                    "TSA_UNTRUSTED_FILE does not exist",
                )

            command.extend(
                [
                    "-untrusted",
                    str(untrusted_path),
                ]
            )

        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        message = (
            result.stdout.strip()
            or result.stderr.strip()
            or f"openssl rc={result.returncode}"
        )

        return (
            result.returncode == 0,
            message,
        )

    except Exception as exc:
        return False, str(exc)

    finally:
        if path:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass


def encode_tsr(
    tsr_bytes: bytes,
) -> str:
    return base64.b64encode(
        tsr_bytes
    ).decode("ascii")


def decode_tsr(
    stored: str,
) -> bytes:
    if not isinstance(stored, str):
        raise TSAError(
            "Stored TSR must be text"
        )

    value = stored.strip()

    if not value:
        raise TSAError(
            "Stored TSR is empty"
        )

    # Backward compatibility:
    # old InLoopID code stored DER as hexadecimal.
    if (
        len(value) % 2 == 0
        and len(value) >= 100
        and re.fullmatch(
            r"[0-9a-fA-F]+",
            value,
        )
    ):
        try:
            return bytes.fromhex(value)
        except ValueError:
            pass

    try:
        return base64.b64decode(
            value,
            validate=True,
        )
    except Exception as exc:
        raise TSAError(
            "Stored TSR is neither valid Base64 "
            "nor legacy hexadecimal DER"
        ) from exc


def verify_tsr(
    content_hash_hex: str,
    stored_tsr: str,
) -> tuple[bool, str]:
    try:
        raw = decode_tsr(
            stored_tsr
        )
    except Exception as exc:
        return False, str(exc)

    return verify_tsr_bytes(
        content_hash_hex,
        raw,
    )


def request_timestamp(
    content_hash_hex: str,
) -> bytes:
    digest = validate_sha256_digest(
        content_hash_hex
    )

    query_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".tsq",
        ) as handle:
            query_path = handle.name

        _run(
            [
                "openssl",
                "ts",
                "-query",
                "-digest",
                digest,
                "-sha256",
                "-cert",
                "-out",
                query_path,
            ]
        )

        with open(
            query_path,
            "rb",
        ) as handle:
            query = handle.read()

        response = requests.post(
            tsa_url(),
            data=query,
            headers={
                "Content-Type":
                    "application/timestamp-query",
                "Accept":
                    "application/timestamp-reply",
            },
            timeout=20,
        )

        response.raise_for_status()

        raw = response.content

        if not raw:
            raise TSAError(
                "TSA returned an empty response"
            )

        ok, message = verify_tsr_bytes(
            digest,
            raw,
        )

        if not ok:
            raise TSAError(
                "TSA response failed cryptographic "
                f"verification: {message}"
            )

        return raw

    finally:
        if query_path:
            try:
                os.remove(query_path)
            except FileNotFoundError:
                pass


def tsr_sha256(
    tsr_bytes: bytes,
) -> str:
    return hashlib.sha256(
        tsr_bytes
    ).hexdigest()
