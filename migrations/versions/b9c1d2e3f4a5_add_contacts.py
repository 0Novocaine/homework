"""Add contacts table.

Revision ID: b9c1d2e3f4a5
Revises: a8b0adbb9140
Create Date: 2026-08-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "b9c1d2e3f4a5"
down_revision: Union[str, Sequence[str], None] = "a8b0adbb9140"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=False),
        sa.Column("birthday", sa.Date(), nullable=False),
        sa.Column("additional_data", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_contacts_first_name", "contacts", ["first_name"])
    op.create_index("ix_contacts_last_name", "contacts", ["last_name"])
    op.create_index("ix_contacts_email", "contacts", ["email"])


def downgrade() -> None:
    op.drop_index("ix_contacts_email", table_name="contacts")
    op.drop_index("ix_contacts_last_name", table_name="contacts")
    op.drop_index("ix_contacts_first_name", table_name="contacts")
    op.drop_table("contacts")
