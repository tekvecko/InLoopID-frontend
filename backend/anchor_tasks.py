import logging
from datetime import UTC, datetime

from celery_app import celery
from tsa_service import (
    encode_tsr,
    request_timestamp,
    tsr_sha256,
    verify_tsr,
)


logger = logging.getLogger(__name__)


def _issue_anchor_tsa(
    task,
    anchor_id: int,
):
    from app import db, create_app
    from models import VerifiableCredentialAnchor

    app = create_app()

    with app.app_context():
        anchor = db.session.get(
            VerifiableCredentialAnchor,
            anchor_id,
        )

        if not anchor:
            logger.error(
                "[TSA] Anchor %s not found",
                anchor_id,
            )
            return False

        try:
            if (
                anchor.tsa_status == "COMPLETED"
                and anchor.eidas_tsr_base64
            ):
                ok, message = verify_tsr(
                    anchor.content_hash,
                    anchor.eidas_tsr_base64,
                )

                if not ok:
                    raise RuntimeError(
                        "Stored completed TSR failed verification: "
                        f"{message}"
                    )

                return True

            anchor.tsa_status = "IN_PROGRESS"
            anchor.tsa_error = None
            db.session.commit()

            raw_tsr = request_timestamp(
                anchor.content_hash
            )

            stored = encode_tsr(
                raw_tsr
            )

            ok, message = verify_tsr(
                anchor.content_hash,
                stored,
            )

            if not ok:
                raise RuntimeError(
                    "RFC3161 verification failed after receipt: "
                    f"{message}"
                )

            now = (
                datetime.now(UTC)
                .replace(tzinfo=None)
            )

            anchor.eidas_tsr_base64 = stored
            anchor.tsa_response_sha256 = (
                tsr_sha256(raw_tsr)
            )
            anchor.tsa_verified_at = now
            anchor.timestamped_at = now
            anchor.tsa_status = "COMPLETED"
            anchor.tsa_error = None

            if anchor.status == "PROCESSING":
                anchor.status = "ISSUED"

            db.session.commit()

            logger.info(
                "[TSA] Anchor %s cryptographically verified",
                anchor_id,
            )

            return True

        except Exception as exc:
            db.session.rollback()

            anchor = db.session.get(
                VerifiableCredentialAnchor,
                anchor_id,
            )

            logger.warning(
                "[TSA] Anchor %s: %s",
                anchor_id,
                exc,
            )

            if (
                anchor is not None
                and task.request.retries >= task.max_retries
            ):
                anchor.tsa_status = "FAILED"
                anchor.tsa_error = str(exc)

                if anchor.status == "PROCESSING":
                    anchor.status = "FAILED"

                db.session.commit()

                return False

            raise task.retry(
                exc=exc
            )


@celery.task(
    bind=True,
    name="anchor.issue_tsa_timestamp",
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
    reject_on_worker_lost=True,
)
def issue_anchor_tsa_timestamp(
    self,
    anchor_id: int,
):
    return _issue_anchor_tsa(
        self,
        anchor_id,
    )
