"""Update vectorId column of t_image_metadata table to store uuid instead of integer

Revision ID: ced2c201d69d
Revises: 5e8b7d47ad31
Create Date: 2025-11-13 18:00:45.250221

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ced2c201d69d"
down_revision: Union[str, Sequence[str], None] = "5e8b7d47ad31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the existing vectorId column
    op.drop_column("t_image_metadata", "vectorId")

    # Add the vectorId column back with UUID type
    op.add_column("t_image_metadata", sa.Column("vectorId", postgresql.UUID(as_uuid=False), nullable=True))

    # Create index for the new vectorId column for better query performance
    op.create_index("ix_t_image_metadata_vectorId", "t_image_metadata", ["vectorId"])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop the index
    op.drop_index("ix_t_image_metadata_vectorId", table_name="t_image_metadata")

    # Drop the UUID vectorId column
    op.drop_column("t_image_metadata", "vectorId")

    # Add back the Integer vectorId column
    op.add_column("t_image_metadata", sa.Column("vectorId", sa.Integer(), nullable=True))
