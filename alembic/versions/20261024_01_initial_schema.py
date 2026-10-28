"""Create the initial PhotoShare schema."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

revision = "20261024_01"
down_revision = None
branch_labels = None
depends_on = None

role = ENUM("USER", "MODERATOR", "ADMIN", name="role", create_type=False)


def upgrade() -> None:
    role.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(100)),
        sa.Column("role", role, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("username"), sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("tags", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("name", sa.String(50), nullable=False), sa.UniqueConstraint("name"))
    op.create_index("ix_tags_name", "tags", ["name"])
    op.create_table(
        "photos",
        sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("description", sa.String(1000)),
        sa.Column("image_url", sa.String(2048), nullable=False), sa.Column("public_id", sa.String(255), nullable=False),
        sa.Column("owner_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("public_id"),
    )
    op.create_index("ix_photos_owner_id", "photos", ["owner_id"])
    op.create_table("photo_tags", sa.Column("photo_id", sa.Uuid(), sa.ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True), sa.Column("tag_id", sa.Uuid(), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True))
    op.create_table(
        "comments", sa.Column("id", sa.Uuid(), primary_key=True), sa.Column("text", sa.String(1000), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("photo_id", sa.Uuid(), sa.ForeignKey("photos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_comments_user_id", "comments", ["user_id"]); op.create_index("ix_comments_photo_id", "comments", ["photo_id"])
    op.create_table(
        "photo_transformations", sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("photo_id", sa.Uuid(), sa.ForeignKey("photos.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(30), nullable=False), sa.Column("options", sa.String(500), nullable=False),
        sa.Column("image_url", sa.String(2048), nullable=False), sa.Column("qr_code", sa.String(2048), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_photo_transformations_photo_id", "photo_transformations", ["photo_id"])


def downgrade() -> None:
    op.drop_table("photo_transformations"); op.drop_table("comments"); op.drop_table("photo_tags"); op.drop_table("photos"); op.drop_table("tags"); op.drop_table("users")
    role.drop(op.get_bind(), checkfirst=True)
