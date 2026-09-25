"""Add user email confirmation status.

Revision ID: d2e3f4a5b6c7
Revises: c1d2e3f4a5b6
Create Date: 2026-09-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d2e3f4a5b6c7"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # server_default ensures existing accounts receive False during migration.
    op.add_column(
        "users",
        sa.Column("confirmed", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("users", "confirmed", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "confirmed")
