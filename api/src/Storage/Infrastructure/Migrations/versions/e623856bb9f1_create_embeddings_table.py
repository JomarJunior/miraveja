"""Create Embeddings Table

Revision ID: e623856bb9f1
Revises: e51ed6a9091e
Create Date: 2025-08-09 15:11:01.184570

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e623856bb9f1'
down_revision: Union[str, Sequence[str], None] = 'e51ed6a9091e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "t_embeddings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("image_id", sa.Integer, sa.ForeignKey("t_images.id", ondelete="CASCADE"), nullable=False),
        sa.Column("embedding", postgresql.ARRAY(sa.Float), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("t_embeddings")
