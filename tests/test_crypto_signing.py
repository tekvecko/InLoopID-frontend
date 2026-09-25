import json
import os

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from crypto_signing import (
    canonical_vc_signing_payload,
    public_jwk_from_key,
    sign_for_identity,
    verify_signature,
)


class Identity:
    pass


def test_real_ed25519_roundtrip(
    tmp_path,
    monkeypatch,
):
    key = Ed25519PrivateKey.generate()

    path = tmp_path / "issuer.pem"

    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

    os.chmod(
        path,
        0o600,
    )

    monkeypatch.setenv(
        "INLOOPID_ED25519_PRIVATE_KEY_FILE",
        str(path),
    )

    # INLOOPID_TEST_PASSWORD_ENV_ISOLATION_V1
    # The test key above is deliberately unencrypted.
    # Do not inherit the production password-file setting.
    monkeypatch.delenv(
        "INLOOPID_ED25519_PRIVATE_KEY_PASSWORD_FILE",
        raising=False,
    )

    identity = Identity()
    identity.public_key_jwk = json.dumps(
        public_jwk_from_key(
            key
        )
    )

    payload = canonical_vc_signing_payload(
        credential_id="c1",
        content_hash="a" * 64,
        issuer_did="did:test:issuer",
        subject_did="did:test:subject",
    )

    signature = sign_for_identity(
        identity,
        payload,
    )

    assert signature.startswith(
        "ed25519:v1:"
    )

    assert verify_signature(
        identity.public_key_jwk,
        payload,
        signature,
    )


def test_encrypted_ed25519_key_roundtrip(
    tmp_path,
    monkeypatch,
):
    key = Ed25519PrivateKey.generate()

    password = b"test-only-password"

    key_path = (
        tmp_path
        / "encrypted-issuer.pem"
    )

    password_path = (
        tmp_path
        / "issuer.pass"
    )

    key_path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=
                serialization.BestAvailableEncryption(
                    password
                ),
        )
    )

    password_path.write_bytes(
        password + b"\n"
    )

    os.chmod(
        key_path,
        0o600,
    )

    os.chmod(
        password_path,
        0o600,
    )

    monkeypatch.setenv(
        "INLOOPID_ED25519_PRIVATE_KEY_FILE",
        str(key_path),
    )

    monkeypatch.setenv(
        "INLOOPID_ED25519_PRIVATE_KEY_PASSWORD_FILE",
        str(password_path),
    )

    identity = Identity()

    identity.public_key_jwk = json.dumps(
        public_jwk_from_key(
            key
        )
    )

    payload = canonical_vc_signing_payload(
        credential_id="encrypted-c1",
        content_hash="e" * 64,
        issuer_did="did:test:encrypted-issuer",
        subject_did="did:test:subject",
    )

    signature = sign_for_identity(
        identity,
        payload,
    )

    assert signature.startswith(
        "ed25519:v1:"
    )

    assert verify_signature(
        identity.public_key_jwk,
        payload,
        signature,
    )

