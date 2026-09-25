import pytest

import app as app_module
import anchor_tasks

from app import create_app
from models import (
    db,
    VerifiableCredentialAnchor,
)


class RetrySignal(Exception):
    pass


class Request:
    retries = 0


class FakeTask:
    max_retries = 3
    request = Request()

    def retry(
        self,
        exc,
    ):
        raise RetrySignal(
            str(exc)
        )


@pytest.fixture
def flask_app(
    tmp_path,
    monkeypatch,
):
    db_path = tmp_path / "tsa.db"

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
        "create_app",
        lambda: app,
    )

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


def add_anchor(
    app,
):
    with app.app_context():
        anchor = VerifiableCredentialAnchor(
            credential_id="tsa-test",
            content_hash="a" * 64,
            status="PROCESSING",
            tsa_status="PENDING",
        )

        db.session.add(anchor)
        db.session.commit()

        return anchor.id


def test_success(
    flask_app,
    monkeypatch,
):
    anchor_id = add_anchor(
        flask_app
    )

    monkeypatch.setattr(
        anchor_tasks,
        "request_timestamp",
        lambda digest: b"verified-tsr",
    )

    monkeypatch.setattr(
        anchor_tasks,
        "verify_tsr",
        lambda digest, stored: (
            True,
            "Verification: OK",
        ),
    )

    assert anchor_tasks._issue_anchor_tsa(
        FakeTask(),
        anchor_id,
    )

    with flask_app.app_context():
        anchor = db.session.get(
            VerifiableCredentialAnchor,
            anchor_id,
        )

        assert anchor.tsa_status == "COMPLETED"
        assert anchor.status == "ISSUED"
        assert anchor.tsa_verified_at is not None
        assert anchor.tsa_response_sha256


def test_retry_keeps_recoverable_state(
    flask_app,
    monkeypatch,
):
    anchor_id = add_anchor(
        flask_app
    )

    def fail(_):
        raise RuntimeError(
            "temporary"
        )

    monkeypatch.setattr(
        anchor_tasks,
        "request_timestamp",
        fail,
    )

    with pytest.raises(
        RetrySignal
    ):
        anchor_tasks._issue_anchor_tsa(
            FakeTask(),
            anchor_id,
        )

    with flask_app.app_context():
        anchor = db.session.get(
            VerifiableCredentialAnchor,
            anchor_id,
        )

        assert anchor.tsa_status == "IN_PROGRESS"
        assert anchor.status == "PROCESSING"


def test_terminal_failure(
    flask_app,
    monkeypatch,
):
    anchor_id = add_anchor(
        flask_app
    )

    def fail(_):
        raise RuntimeError(
            "permanent"
        )

    monkeypatch.setattr(
        anchor_tasks,
        "request_timestamp",
        fail,
    )

    task = FakeTask()
    task.request.retries = 3

    assert not anchor_tasks._issue_anchor_tsa(
        task,
        anchor_id,
    )

    with flask_app.app_context():
        anchor = db.session.get(
            VerifiableCredentialAnchor,
            anchor_id,
        )

        assert anchor.tsa_status == "FAILED"
        assert anchor.status == "FAILED"


def test_missing_anchor(
    flask_app,
):
    assert not anchor_tasks._issue_anchor_tsa(
        FakeTask(),
        999999,
    )
