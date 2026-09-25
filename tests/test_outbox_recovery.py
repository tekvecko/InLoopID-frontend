from datetime import timedelta

import pytest

import app as app_module
import hr_tasks
import outbox_tasks

from app import create_app
from models import (
    db,
    OutboxEvent,
    VerifiableCredentialAnchor,
)
from outbox_service import (
    ensure_outbox_event,
    utcnow_naive,
)


@pytest.fixture
def flask_app(
    tmp_path,
    monkeypatch,
):
    db_path = (
        tmp_path
        / "outbox-recovery.db"
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


def test_stale_dispatched_event_is_recovered(
    flask_app,
    monkeypatch,
):
    calls = []

    def fake_apply_async(
        *,
        args,
        task_id,
        queue,
    ):
        calls.append(
            {
                "args": args,
                "task_id": task_id,
                "queue": queue,
            }
        )

        class Result:
            id = task_id

        return Result()

    monkeypatch.setattr(
        hr_tasks.issue_hr_contract_vc_async,
        "apply_async",
        fake_apply_async,
    )

    with flask_app.app_context():
        anchor = VerifiableCredentialAnchor(
            credential_id="outbox-recovery-contract",
            content_hash="c" * 64,
            status="PROCESSING",
            tsa_status="PENDING",
        )

        db.session.add(anchor)
        db.session.flush()

        event = ensure_outbox_event(
            session=db.session,
            event_type="HR_ISSUE_REQUESTED",
            aggregate_type=(
                "VerifiableCredentialAnchor"
            ),
            aggregate_id=anchor.id,
            dedup_key=f"hr-issue:{anchor.id}",
            payload={
                "credential_id":
                    anchor.credential_id,
            },
        )

        db.session.commit()

        event_id = event.id
        logical_task_id = event.event_id

        result1 = (
            outbox_tasks
            .dispatch_outbox_events
            .run()
        )

        assert result1["dispatched"] == 1
        assert len(calls) == 1

        db.session.expire_all()

        event = db.session.get(
            OutboxEvent,
            event_id,
        )

        assert event.status == "DISPATCHED"
        assert event.attempts == 1

        # Simulate:
        #
        # broker accepted the message,
        # process then died before outcome became visible.
        event.dispatched_at = (
            utcnow_naive()
            - timedelta(
                seconds=(
                    outbox_tasks.STALE_SECONDS
                    + 1
                )
            )
        )

        db.session.commit()

        result2 = (
            outbox_tasks
            .dispatch_outbox_events
            .run()
        )

        assert result2["dispatched"] == 1
        assert len(calls) == 2

        # Logical task id is stable across recovery.
        assert calls[0]["task_id"] == (
            logical_task_id
        )

        assert calls[1]["task_id"] == (
            logical_task_id
        )

        db.session.expire_all()

        event = db.session.get(
            OutboxEvent,
            event_id,
        )

        assert event.status == "DISPATCHED"
        assert event.attempts == 2
