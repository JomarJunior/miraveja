"""Create members table for storing extra data about the users

Revision ID: 4be0571e9868
Revises: 821aebd9f19f
Create Date: 2025-10-03 18:03:31.150849

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from MiravejaApi.Member.Infrastructure.Sql.Entities import MemberEntity

# revision identifiers, used by Alembic.
revision: str = "4be0571e9868"
down_revision: Union[str, Sequence[str], None] = "821aebd9f19f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        MemberEntity.__tablename__,
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("first_name", sa.String(length=50), nullable=False),
        sa.Column("last_name", sa.String(length=50), nullable=False),
        sa.Column("registered_at", sa.DateTime, nullable=False, server_default=sa.text("now()")),
        sa.Column(
            "updated_at", sa.DateTime, nullable=False, server_default=sa.text("now()"), onupdate=sa.text("now()")
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(MemberEntity.__tablename__)
