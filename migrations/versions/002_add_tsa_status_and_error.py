"""add tsa_status and tsa_error to verifiable_credential_anchors

Revision ID: 002_add_tsa_status_and_error
Revises:
Create Date: 2026-09-21 09:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '002_add_tsa_status_and_error'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    Přidání sloupců tsa_status a tsa_error do tabulky verifiable_credential_anchors.
    """
    with op.batch_alter_table('verifiable_credential_anchors', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'tsa_status',
                sa.String(length=32),
                nullable=False,
                server_default='COMPLETED',
                comment='Stav asynchronního eIDAS TSA razítkování (PENDING, COMPLETED, FAILED)'
            )
        )
        batch_op.add_column(
            sa.Column(
                'tsa_error',
                sa.Text(),
                nullable=True,
                comment='Detail chybové hlášky při selhání TSA razítkování'
            )
        )


def downgrade():
    """
    Odstranění sloupců tsa_status a tsa_error.
    """
    with op.batch_alter_table('verifiable_credential_anchors', schema=None) as batch_op:
        batch_op.drop_column('tsa_error')
        batch_op.drop_column('tsa_status')
