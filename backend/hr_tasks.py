import os

from celery_app import celery


@celery.task(
    bind=True,
    name="hr.issue_vc_async",
    acks_late=True,
    reject_on_worker_lost=True,
)
def issue_hr_contract_vc_async(
    self,
    credential_id,
):
    from app import app
    from crypto_signing import (
        canonical_vc_signing_payload,
        sign_for_identity,
    )
    from models import (
        db,
        IdentityNode,
        VerifiableCredentialAnchor,
    )
    from outbox_service import (
        ensure_outbox_event,
    )

    with app.app_context():
        anchor = (
            VerifiableCredentialAnchor.query
            .filter_by(
                credential_id=credential_id
            )
            .first()
        )

        if not anchor:
            return {
                "status": "error",
                "message": (
                    f"Kredenciál {credential_id} nenalezen"
                ),
            }

        if (
            anchor.status == "ISSUED"
            and anchor.tsa_status == "COMPLETED"
            and anchor.proof_signature
            and anchor.proof_signature.startswith(
                "ed25519:v1:"
            )
        ):
            return {
                "status": "success",
                "already_completed": True,
                "credential_id": credential_id,
            }

        try:
            if not anchor.subject_did:
                raise ValueError(
                    "HR contract has no subject DID"
                )

            subject = (
                IdentityNode.query
                .filter_by(
                    tenant_id=anchor.tenant_id,
                    did_uri=anchor.subject_did,
                    is_active=True,
                )
                .first()
            )

            if not subject:
                raise ValueError(
                    "Registered active HR subject "
                    "identity not found"
                )

            # INLOOPID_EXPLICIT_ISSUER_DID_V1
            #
            # Signing authority must always be selected
            # explicitly by deployment configuration.
            # Never silently substitute an issuer DID.
            issuer_did = os.getenv(
                "ISSUER_DID"
            )

            if (
                issuer_did is None
                or not issuer_did.strip()
            ):
                raise ValueError(
                    "ISSUER_DID is required for "
                    "HR credential signing"
                )

            issuer_did = issuer_did.strip()

            issuer = (
                IdentityNode.query
                .filter_by(
                    tenant_id=anchor.tenant_id,
                    did_uri=issuer_did,
                    is_active=True,
                )
                .first()
            )

            if not issuer:
                raise ValueError(
                    "Registered active HR issuer "
                    "identity not found"
                )

            payload = canonical_vc_signing_payload(
                credential_id=anchor.credential_id,
                content_hash=anchor.content_hash,
                issuer_did=issuer.did_uri,
                subject_did=anchor.subject_did,
            )

            signature = sign_for_identity(
                issuer,
                payload,
            )

            anchor.issuer_did = issuer.did_uri
            anchor.proof_signature = signature
            anchor.status = "PROCESSING"

            if anchor.tsa_status != "COMPLETED":
                anchor.tsa_status = "PENDING"

            anchor.tsa_error = None

            event = ensure_outbox_event(
                session=db.session,
                event_type="TSA_REQUESTED",
                aggregate_type="VerifiableCredentialAnchor",
                aggregate_id=anchor.id,
                dedup_key=f"tsa:{anchor.id}",
                payload={
                    "anchor_id": anchor.id,
                },
            )

            db.session.commit()

            return {
                "status": "success",
                "credential_id": credential_id,
                "anchor_status": anchor.status,
                "tsa_status": anchor.tsa_status,
                "issuer_did": anchor.issuer_did,
                "tsa_outbox_event_id": event.event_id,
            }

        except Exception as exc:
            db.session.rollback()

            anchor = db.session.get(
                VerifiableCredentialAnchor,
                anchor.id,
            )

            if anchor is not None:
                anchor.status = "FAILED"
                anchor.tsa_status = "FAILED"
                anchor.tsa_error = str(exc)
                db.session.commit()

            return {
                "status": "error",
                "message": str(exc),
            }
