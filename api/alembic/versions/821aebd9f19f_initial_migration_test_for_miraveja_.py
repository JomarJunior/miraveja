"""Initial migration test for MiraVeja environment

Revision ID: 821aebd9f19f
Revises:
Create Date: 2025-10-03 17:48:31.108586

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "821aebd9f19f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Just executing a simple command to test the migration setup
    op.execute("SELECT 1")


def downgrade() -> None:
    """Downgrade schema."""
    # Just executing a simple command to test the migration setup
    op.execute("SELECT 2")
