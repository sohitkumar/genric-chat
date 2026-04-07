"""add optional user_id to messages

Revision ID: 002_messages_user_id
Revises: 001_initial
Create Date: 2026-04-07

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_messages_user_id"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "messages",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "messages_user_id_fkey",
        "messages",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("messages_user_id_fkey", "messages", type_="foreignkey")
    op.drop_column("messages", "user_id")
