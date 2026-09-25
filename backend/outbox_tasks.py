from __future__ import annotations

import json
import os
from datetime import timedelta

from celery_app import celery


STALE_SECONDS = int(
    os.getenv(
        "INLOOPID_OUTBOX_STALE_SECONDS",
        "120",
    )
)


def _target_complete(
    db,
    event,
) -> bool:
    from models import (
        OutboxEvent,
        VerifiableCredentialAnchor,
    )

    anchor = db.session.get(
        VerifiableCredentialAnchor,
        event.aggregate_id,
    )

    if not anchor:
        return False

    if event.event_type == "HR_ISSUE_REQUESTED":
        tsa_event = (
            OutboxEvent.query
            .filter_by(
                dedup_key=f"tsa:{anchor.id}"
            )
            .first()
        )

        return bool(
            anchor.proof_signature
            and anchor.proof_signature.startswith(
                "ed25519:v1:"
            )
            and tsa_event
        )

    if event.event_type == "TSA_REQUESTED":
        return bool(
            anchor.tsa_status == "COMPLETED"
            and anchor.eidas_tsr_base64
            and anchor.tsa_verified_at
        )

    return False


def _dispatch(
    event,
):
    payload = json.loads(
        event.payload_json
    )

    task_id = event.event_id

    if event.event_type == "HR_ISSUE_REQUESTED":
        from hr_tasks import (
            issue_hr_contract_vc_async,
        )

        return (
            issue_hr_contract_vc_async
            .apply_async(
                args=[
                    payload["credential_id"]
                ],
                task_id=task_id,
                queue=os.getenv(
                    "CELERY_TASK_DEFAULT_QUEUE",
                    "celery",
                ),
            )
        )

    if event.event_type == "TSA_REQUESTED":
        from anchor_tasks import (
            issue_anchor_tsa_timestamp,
        )

        return (
            issue_anchor_tsa_timestamp
            .apply_async(
                args=[
                    int(payload["anchor_id"])
                ],
                task_id=task_id,
                queue=os.getenv(
                    "CELERY_TASK_DEFAULT_QUEUE",
                    "celery",
                ),
            )
        )

    raise ValueError(
        f"Unsupported outbox event type: {event.event_type}"
    )


@celery.task(
    name="outbox.dispatch",
    acks_late=True,
    reject_on_worker_lost=True,
)
def dispatch_outbox_events():
    from app import app
    from models import db, OutboxEvent
    from outbox_service import utcnow_naive

    dispatched = 0
    completed = 0
    failed = 0

    with app.app_context():
        now = utcnow_naive()

        events = (
            OutboxEvent.query
            .filter(
                OutboxEvent.status.in_(
                    [
                        "PENDING",
                        "DISPATCHED",
                    ]
                )
            )
            .order_by(
                OutboxEvent.id.asc()
            )
            .limit(100)
            .all()
        )

        for event in events:
            try:
                if _target_complete(
                    db,
                    event,
                ):
                    event.status = "COMPLETED"
                    event.completed_at = now
                    event.last_error = None
                    db.session.commit()

                    completed += 1
                    continue

                if event.status == "DISPATCHED":
                    if not event.dispatched_at:
                        event.status = "PENDING"

                    elif (
                        now
                        - event.dispatched_at
                    ) < timedelta(
                        seconds=STALE_SECONDS
                    ):
                        continue

                    else:
                        # At-least-once recovery.
                        event.status = "PENDING"
                        event.available_at = now
                        db.session.commit()

                if (
                    event.available_at
                    and event.available_at > now
                ):
                    continue

                _dispatch(
                    event
                )

                event.attempts += 1
                event.status = "DISPATCHED"
                event.dispatched_at = now
                event.last_error = None

                db.session.commit()

                dispatched += 1

            except Exception as exc:
                db.session.rollback()

                event = db.session.get(
                    OutboxEvent,
                    event.id,
                )

                if event is None:
                    continue

                event.attempts += 1
                event.status = "PENDING"
                event.last_error = str(exc)

                delay = min(
                    300,
                    max(
                        5,
                        2 ** min(
                            event.attempts,
                            8,
                        ),
                    ),
                )

                event.available_at = (
                    utcnow_naive()
                    + timedelta(
                        seconds=delay
                    )
                )

                db.session.commit()

                failed += 1

    return {
        "dispatched": dispatched,
        "completed": completed,
        "failed": failed,
    }
