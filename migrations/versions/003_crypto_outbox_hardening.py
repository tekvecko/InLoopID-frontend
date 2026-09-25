"""crypto outbox hardening

Revision ID: 003_crypto_outbox_hardening
Revises: 002_add_tsa_status_and_error
"""

from alembic import op
import sqlalchemy as sa


revision = "003_crypto_outbox_hardening"
down_revision = "002_add_tsa_status_and_error"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
        "verifiable_credential_anchors"
    ) as batch:
        batch.add_column(
            sa.Column(
                "tsa_verified_at",
                sa.DateTime(),
                nullable=True,
            )
        )
        batch.add_column(
            sa.Column(
                "tsa_response_sha256",
                sa.String(length=64),
                nullable=True,
            )
        )

    op.create_table(
        "outbox_events",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "event_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "dedup_key",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "event_type",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "aggregate_type",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "aggregate_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "payload_json",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "attempts",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "available_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "dispatched_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "last_error",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "id"
        ),
        sa.UniqueConstraint(
            "event_id"
        ),
        sa.UniqueConstraint(
            "dedup_key"
        ),
    )

    op.create_index(
        "ix_outbox_events_event_type",
        "outbox_events",
        ["event_type"],
        unique=False,
    )

    op.create_index(
        "ix_outbox_events_status",
        "outbox_events",
        ["status"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        "ix_outbox_events_status",
        table_name="outbox_events",
    )

    op.drop_index(
        "ix_outbox_events_event_type",
        table_name="outbox_events",
    )

    op.drop_table(
        "outbox_events"
    )

    with op.batch_alter_table(
        "verifiable_credential_anchors"
    ) as batch:
        batch.drop_column(
            "tsa_response_sha256"
        )
        batch.drop_column(
            "tsa_verified_at"
        )
