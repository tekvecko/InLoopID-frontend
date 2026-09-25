import json
import os

import pytest

import app as app_module

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from app import create_app
from crypto_signing import (
    canonical_vc_signing_payload,
    public_jwk_from_key,
    verify_signature,
)
from hr_tasks import (
    issue_hr_contract_vc_async,
)
from models import (
    db,
    IdentityNode,
    OutboxEvent,
    VerifiableCredentialAnchor,
)


@pytest.fixture
def flask_app(
    tmp_path,
    monkeypatch,
):
    db_path = (
        tmp_path
        / "hr-tsa-outbox.db"
    )

    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI":
                f"sqlite:///{db_path}",
            "SQLALCHEMY_ENGINE_OPTIONS": {},
        }
    )

    monkeypatch.setattr(
        app_module,
        "app",
        app,
    )

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


def provision_signer(
    tmp_path,
    monkeypatch,
):
    key = Ed25519PrivateKey.generate()

    path = (
        tmp_path
        / "hr-issuer-ed25519.pem"
    )

    path.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=
                serialization.NoEncryption(),
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

    monkeypatch.delenv(
        "INLOOPID_ED25519_PRIVATE_KEY_PASSWORD_FILE",
        raising=False,
    )

    monkeypatch.setenv(
        "ISSUER_DID",
        "did:inloopid:hr_department_01",
    )

    return key


def create_fixture_data(
    app,
    key,
):
    issuer_jwk = json.dumps(
        public_jwk_from_key(
            key
        ),
        sort_keys=True,
    )

    with app.app_context():
        subject = IdentityNode(
            tenant_id="tenant_test",
            did_uri=(
                "did:inloopid:"
                "employee@example.com"
            ),
            public_key_jwk="{}",
            role="employee",
            is_active=True,
        )

        issuer = IdentityNode(
            tenant_id="tenant_test",
            did_uri=(
                "did:inloopid:"
                "hr_department_01"
            ),
            public_key_jwk=issuer_jwk,
            role="issuer",
            is_active=True,
        )

        anchor = VerifiableCredentialAnchor(
            tenant_id="tenant_test",
            credential_id=(
                "contract-outbox-test"
            ),
            subject_did=(
                "did:inloopid:"
                "employee@example.com"
            ),
            content_hash="a" * 64,
            encrypted_payload="ciphertext",
            status="PROCESSING",
            tsa_status="PENDING",
        )

        db.session.add_all(
            [
                subject,
                issuer,
                anchor,
            ]
        )

        db.session.commit()

        return (
            anchor.id,
            issuer_jwk,
        )


def test_hr_task_creates_real_signature_and_tsa_outbox(
    flask_app,
    tmp_path,
    monkeypatch,
):
    key = provision_signer(
        tmp_path,
        monkeypatch,
    )

    anchor_id, issuer_jwk = (
        create_fixture_data(
            flask_app,
            key,
        )
    )

    with flask_app.app_context():
        anchor = db.session.get(
            VerifiableCredentialAnchor,
            anchor_id,
        )

        result = (
            issue_hr_contract_vc_async.run(
                anchor.credential_id
            )
        )

        db.session.expire_all()

        saved = db.session.get(
            VerifiableCredentialAnchor,
            anchor_id,
        )

        event = (
            OutboxEvent.query
            .filter_by(
                dedup_key=f"tsa:{anchor_id}"
            )
            .one()
        )

        assert result["status"] == "success"

        assert saved.proof_signature.startswith(
            "ed25519:v1:"
        )

        assert saved.status == "PROCESSING"
        assert saved.tsa_status == "PENDING"

        # No TSA value is fabricated by the HR task.
        assert saved.eidas_tsr_base64 is None
        assert saved.timestamped_at is None
        assert saved.tsa_verified_at is None

        assert event.event_type == "TSA_REQUESTED"
        assert event.status == "PENDING"

        payload = canonical_vc_signing_payload(
            credential_id=saved.credential_id,
            content_hash=saved.content_hash,
            issuer_did=saved.issuer_did,
            subject_did=saved.subject_did,
        )

        assert verify_signature(
            issuer_jwk,
            payload,
            saved.proof_signature,
        )


def test_hr_task_is_idempotent_for_tsa_outbox(
    flask_app,
    tmp_path,
    monkeypatch,
):
    key = provision_signer(
        tmp_path,
        monkeypatch,
    )

    anchor_id, _ = create_fixture_data(
        flask_app,
        key,
    )

    with flask_app.app_context():
        anchor = db.session.get(
            VerifiableCredentialAnchor,
            anchor_id,
        )

        first = issue_hr_contract_vc_async.run(
            anchor.credential_id
        )

        second = issue_hr_contract_vc_async.run(
            anchor.credential_id
        )

        assert first["status"] == "success"
        assert second["status"] == "success"

        events = (
            OutboxEvent.query
            .filter_by(
                dedup_key=f"tsa:{anchor_id}"
            )
            .all()
        )

        assert len(events) == 1


def test_hr_task_fails_closed_without_registered_issuer(
    flask_app,
    monkeypatch,
):
    monkeypatch.setenv(
        "ISSUER_DID",
        "did:inloopid:missing",
    )

    with flask_app.app_context():
        subject = IdentityNode(
            tenant_id="tenant_test",
            did_uri=(
                "did:inloopid:"
                "employee@example.com"
            ),
            public_key_jwk="{}",
            role="employee",
            is_active=True,
        )

        anchor = VerifiableCredentialAnchor(
            tenant_id="tenant_test",
            credential_id="contract-missing-issuer",
            subject_did=subject.did_uri,
            content_hash="b" * 64,
            status="PROCESSING",
            tsa_status="PENDING",
        )

        db.session.add_all(
            [
                subject,
                anchor,
            ]
        )

        db.session.commit()

        result = issue_hr_contract_vc_async.run(
            anchor.credential_id
        )

        db.session.expire_all()

        saved = db.session.get(
            VerifiableCredentialAnchor,
            anchor.id,
        )

        assert result["status"] == "error"
        assert saved.status == "FAILED"
        assert saved.tsa_status == "FAILED"

        assert not OutboxEvent.query.filter_by(
            dedup_key=f"tsa:{anchor.id}"
        ).first()


def test_hr_task_requires_explicit_issuer_did(
    flask_app,
    monkeypatch,
):
    monkeypatch.delenv(
        "ISSUER_DID",
        raising=False,
    )

    monkeypatch.delenv(
        "INLOOPID_ED25519_PRIVATE_KEY_FILE",
        raising=False,
    )

    with flask_app.app_context():
        subject = IdentityNode(
            tenant_id="tenant_test",
            did_uri=(
                "did:inloopid:"
                "employee-no-issuer@example.com"
            ),
            public_key_jwk="{}",
            role="employee",
            is_active=True,
        )

        anchor = VerifiableCredentialAnchor(
            tenant_id="tenant_test",
            credential_id=(
                "contract-explicit-issuer-required"
            ),
            subject_did=subject.did_uri,
            content_hash="d" * 64,
            status="PROCESSING",
            tsa_status="PENDING",
        )

        db.session.add_all(
            [
                subject,
                anchor,
            ]
        )

        db.session.commit()

        anchor_id = anchor.id

        result = (
            issue_hr_contract_vc_async.run(
                anchor.credential_id
            )
        )

        db.session.expire_all()

        saved = db.session.get(
            VerifiableCredentialAnchor,
            anchor_id,
        )

        assert result["status"] == "error"

        assert result["message"] == (
            "ISSUER_DID is required for "
            "HR credential signing"
        )

        assert saved.status == "FAILED"
        assert saved.tsa_status == "FAILED"

        assert saved.proof_signature is None

        assert (
            OutboxEvent.query
            .filter_by(
                dedup_key=f"tsa:{anchor_id}"
            )
            .first()
            is None
        )

