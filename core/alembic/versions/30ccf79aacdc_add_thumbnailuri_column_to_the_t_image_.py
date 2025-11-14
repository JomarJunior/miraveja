"""Add thumbnailUri column to the t_image_metadata table

Revision ID: 30ccf79aacdc
Revises: ced2c201d69d
Create Date: 2025-11-13 18:23:27.786393

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "30ccf79aacdc"
down_revision: Union[str, Sequence[str], None] = "ced2c201d69d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add thumbnailUri column to t_image_metadata table
    op.add_column("t_image_metadata", sa.Column("thumbnailUri", sa.String(length=500), nullable=True))

    # Create index for better query performance
    op.create_index("ix_t_image_metadata_thumbnailUri", "t_image_metadata", ["thumbnailUri"])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the index
    op.drop_index("ix_t_image_metadata_thumbnailUri", table_name="t_image_metadata")

    # Drop the thumbnailUri column
    op.drop_column("t_image_metadata", "thumbnailUri")
