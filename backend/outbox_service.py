from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from models import OutboxEvent


def utcnow_naive():
    return datetime.now(
        UTC
    ).replace(
        tzinfo=None
    )


def ensure_outbox_event(
    *,
    session,
    event_type: str,
    aggregate_type: str,
    aggregate_id: int,
    dedup_key: str,
    payload: dict,
):
    existing = (
        session.query(
            OutboxEvent
        )
        .filter_by(
            dedup_key=dedup_key
        )
        .first()
    )

    if existing:
        return existing

    event = OutboxEvent(
        event_id=str(
            uuid.uuid4()
        ),
        dedup_key=dedup_key,
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload_json=json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ),
        status="PENDING",
        attempts=0,
        available_at=utcnow_naive(),
    )

    session.add(event)
    session.flush()

    return event
