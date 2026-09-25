"""Expand refresh token column.

Revision ID: e3f4a5b6c7d
Revises: d2e3f4a5b6c7
Create Date: 2026-09-25
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "e3f4a5b6c7d"
down_revision: Union[str, Sequence[str], None] = "d2e3f4a5b6c7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "refresh_token",
        existing_type=sa.String(length=255),
        type_=sa.String(length=512),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "refresh_token",
        existing_type=sa.String(length=512),
        type_=sa.String(length=255),
        existing_nullable=True,
    )
