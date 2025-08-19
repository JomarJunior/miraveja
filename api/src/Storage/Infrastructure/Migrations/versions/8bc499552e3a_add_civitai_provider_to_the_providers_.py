"""Add CIVITAI provider to the providers table

Revision ID: 8bc499552e3a
Revises: e623856bb9f1
Create Date: 2025-08-19 13:27:46.896531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '8bc499552e3a'
down_revision: Union[str, Sequence[str], None] = 'e623856bb9f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add the CIVITAI provider to the PROVIDERS table
    op.execute(
        "INSERT INTO t_providers (name) VALUES ('CIVITAI')"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "DELETE FROM t_providers WHERE name = 'CIVITAI'"
    )
