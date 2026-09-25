from __future__ import annotations

import base64
import hmac
import json
import os
import stat
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


class SigningError(RuntimeError):
    pass


def _b64url(
    value: bytes,
) -> str:
    return (
        base64.urlsafe_b64encode(value)
        .rstrip(b"=")
        .decode("ascii")
    )


def canonical_vc_signing_payload(
    *,
    credential_id: str,
    content_hash: str,
    issuer_did: str,
    subject_did: str,
) -> bytes:
    obj = {
        "credential_id": credential_id,
        "content_hash": content_hash,
        "issuer_did": issuer_did,
        "subject_did": subject_did,
    }

    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _secure_file(
    env_name: str,
) -> Path:
    raw = os.getenv(env_name)

    if not raw:
        raise SigningError(
            f"{env_name} is not configured"
        )

    path = (
        Path(raw)
        .expanduser()
        .resolve()
    )

    if not path.is_file():
        raise SigningError(
            f"{env_name} does not point to a file"
        )

    mode = stat.S_IMODE(
        path.stat().st_mode
    )

    if mode & 0o077:
        raise SigningError(
            f"{path} permissions are too broad; "
            "expected 0600 or stricter"
        )

    return path


def _password() -> bytes | None:
    raw = os.getenv(
        "INLOOPID_ED25519_PRIVATE_KEY_PASSWORD_FILE"
    )

    if not raw:
        return None

    path = (
        Path(raw)
        .expanduser()
        .resolve()
    )

    if not path.is_file():
        raise SigningError(
            "Private-key password file missing"
        )

    mode = stat.S_IMODE(
        path.stat().st_mode
    )

    if mode & 0o077:
        raise SigningError(
            "Private-key password file permissions "
            "must be 0600 or stricter"
        )

    value = path.read_bytes().rstrip(
        b"\r\n"
    )

    if not value:
        raise SigningError(
            "Private-key password file is empty"
        )

    return value


def load_private_key() -> Ed25519PrivateKey:
    path = _secure_file(
        "INLOOPID_ED25519_PRIVATE_KEY_FILE"
    )

    try:
        key = serialization.load_pem_private_key(
            path.read_bytes(),
            password=_password(),
        )
    except Exception as exc:
        raise SigningError(
            "Unable to load issuer private key"
        ) from exc

    if not isinstance(
        key,
        Ed25519PrivateKey,
    ):
        raise SigningError(
            "Configured issuer key is not Ed25519"
        )

    return key


def public_jwk_from_key(
    key: Ed25519PrivateKey,
) -> dict:
    raw = (
        key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )

    return {
        "kty": "OKP",
        "crv": "Ed25519",
        "x": _b64url(raw),
    }


def validate_identity_key(
    identity,
    key: Ed25519PrivateKey,
) -> None:
    try:
        jwk = json.loads(
            identity.public_key_jwk
        )
    except Exception as exc:
        raise SigningError(
            "Identity public_key_jwk is not valid JSON"
        ) from exc

    expected = public_jwk_from_key(
        key
    )

    if (
        jwk.get("kty") != "OKP"
        or jwk.get("crv") != "Ed25519"
        or not isinstance(
            jwk.get("x"),
            str,
        )
    ):
        raise SigningError(
            "Issuer IdentityNode does not contain "
            "an Ed25519 OKP public JWK"
        )

    if not hmac.compare_digest(
        jwk["x"],
        expected["x"],
    ):
        raise SigningError(
            "Configured Ed25519 private key does not "
            "match issuer IdentityNode.public_key_jwk"
        )


def sign_for_identity(
    identity,
    payload: bytes,
) -> str:
    key = load_private_key()

    validate_identity_key(
        identity,
        key,
    )

    signature = key.sign(
        payload
    )

    return (
        "ed25519:v1:"
        + _b64url(signature)
    )


def verify_signature(
    public_jwk: str,
    payload: bytes,
    stored_signature: str,
) -> bool:
    prefix = "ed25519:v1:"

    if not stored_signature.startswith(
        prefix
    ):
        return False

    try:
        jwk = json.loads(
            public_jwk
        )

        if (
            jwk.get("kty") != "OKP"
            or jwk.get("crv") != "Ed25519"
        ):
            return False

        raw_public = base64.urlsafe_b64decode(
            jwk["x"]
            + "=" * (
                (-len(jwk["x"])) % 4
            )
        )

        signature_text = stored_signature[
            len(prefix):
        ]

        signature = base64.urlsafe_b64decode(
            signature_text
            + "=" * (
                (-len(signature_text)) % 4
            )
        )

        key = Ed25519PublicKey.from_public_bytes(
            raw_public
        )

        key.verify(
            signature,
            payload,
        )

        return True

    except Exception:
        return False
