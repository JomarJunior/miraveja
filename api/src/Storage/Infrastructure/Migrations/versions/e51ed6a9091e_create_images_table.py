"""Create Images Table and all related tables

Revision ID: e51ed6a9091e
Revises:
Create Date: 2025-08-09 14:10:05.618463

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import event, DDL
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "e51ed6a9091e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create the PROVIDERS table
    op.create_table(
        "t_providers",
        sa.Column(
            "id", sa.Integer, primary_key=True, autoincrement=True
        ),  # Unique identifier for each provider
        sa.Column(
            "name", sa.String(length=100), nullable=False
        ),  # Name of the provider
    )

    # Create the IMAGES table
    op.create_table(
        "t_images",
        sa.Column(
            "id", sa.Integer, primary_key=True, autoincrement=True
        ),  # Unique identifier for each image
        sa.Column(
            "uri", sa.String(length=255), nullable=False
        ),  # A path in the filesystem or a URL
        sa.Column(
            "image_metadata", postgresql.JSONB, nullable=False
        ),  # Metadata associated with the image (not structured)
        sa.Column(
            "provider_id",
            sa.Integer,
            sa.ForeignKey("t_providers.id", ondelete="CASCADE"),
            nullable=False,
        ),  # Foreign key to the provider
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("t_images")
    op.drop_table("t_providers")
