"""Add users and assign contacts to their owners.

Revision ID: c1d2e3f4a5b6
Revises: b9c1d2e3f4a5
Create Date: 2026-08-25
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, Sequence[str], None] = "b9c1d2e3f4a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=250), nullable=False),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("avatar", sa.String(length=255), nullable=True),
        sa.Column("refresh_token", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    # Nullable preserves contacts created before authentication was introduced.
    # Such legacy records are not returned by the authenticated API.
    op.add_column("contacts", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_contacts_user_id_users", "contacts", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index("ix_contacts_user_id", "contacts", ["user_id"])

    op.add_column("notes", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_notes_user_id_users", "notes", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index("ix_notes_user_id", "notes", ["user_id"])

    # The old schema made tag names globally unique. Tags are now private to a
    # user, so the same tag name may belong to different users.
    op.drop_constraint("tags_name_key", "tags", type_="unique")
    op.add_column("tags", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_tags_user_id_users", "tags", "users", ["user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index("ix_tags_user_id", "tags", ["user_id"])
    op.create_unique_constraint("unique_tag_user", "tags", ["name", "user_id"])


def downgrade() -> None:
    op.drop_constraint("unique_tag_user", "tags", type_="unique")
    op.drop_index("ix_tags_user_id", table_name="tags")
    op.drop_constraint("fk_tags_user_id_users", "tags", type_="foreignkey")
    op.drop_column("tags", "user_id")
    op.create_unique_constraint("tags_name_key", "tags", ["name"])

    op.drop_index("ix_notes_user_id", table_name="notes")
    op.drop_constraint("fk_notes_user_id_users", "notes", type_="foreignkey")
    op.drop_column("notes", "user_id")

    op.drop_index("ix_contacts_user_id", table_name="contacts")
    op.drop_constraint("fk_contacts_user_id_users", "contacts", type_="foreignkey")
    op.drop_column("contacts", "user_id")
    op.drop_table("users")
