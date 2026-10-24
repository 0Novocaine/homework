"""Create initial PhotoShare schema."""

from alembic import op
from app.db.base import Base
import app.models  # noqa: F401

revision = "20261024_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
