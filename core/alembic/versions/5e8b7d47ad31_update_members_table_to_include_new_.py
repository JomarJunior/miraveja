"""Update Members table to include new enriched member data structure

Revision ID: 5e8b7d47ad31
Revises: 9ff1299684b3
Create Date: 2025-11-04 00:50:14.599680

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "5e8b7d47ad31"
down_revision: Union[str, Sequence[str], None] = "9ff1299684b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to include enriched member data structure."""
    # Profile fields
    op.add_column(
        "t_member",
        sa.Column(
            "username",
            sa.String(length=41),
            nullable=False,
            server_default=sa.text("'user_' || gen_random_uuid()::text"),
        ),
    )
    op.add_column("t_member", sa.Column("bio", sa.String(length=500), nullable=False, server_default=""))
    op.add_column("t_member", sa.Column("avatar_id", sa.Integer(), nullable=True))
    op.add_column("t_member", sa.Column("cover_id", sa.Integer(), nullable=True))

    # Identity fields (first_name and last_name already exist)
    op.add_column("t_member", sa.Column("gender", sa.String(length=50), nullable=True))
    op.add_column("t_member", sa.Column("date_of_birth", sa.DateTime(timezone=True), nullable=True))

    # Social fields (stored as JSONB arrays)
    op.add_column(
        "t_member", sa.Column("friends", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]")
    )
    op.add_column(
        "t_member", sa.Column("followers", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]")
    )
    op.add_column(
        "t_member", sa.Column("following", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]")
    )

    # Member state
    op.add_column("t_member", sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"))

    # Add unique constraint on username
    op.create_unique_constraint("uq_member_username", "t_member", ["username"])

    # Add foreign key constraints for avatar and cover images
    op.create_foreign_key(
        "fk_member_avatar_id", "t_member", "t_image_metadata", ["avatar_id"], ["id"], ondelete="SET NULL"
    )
    op.create_foreign_key(
        "fk_member_cover_id", "t_member", "t_image_metadata", ["cover_id"], ["id"], ondelete="SET NULL"
    )


def downgrade() -> None:
    """Downgrade schema to original member structure."""
    # Drop foreign keys first
    op.drop_constraint("fk_member_cover_id", "t_member", type_="foreignkey")
    op.drop_constraint("fk_member_avatar_id", "t_member", type_="foreignkey")

    # Drop unique constraint
    op.drop_constraint("uq_member_username", "t_member", type_="unique")

    # Drop new columns
    op.drop_column("t_member", "is_active")
    op.drop_column("t_member", "following")
    op.drop_column("t_member", "followers")
    op.drop_column("t_member", "friends")
    op.drop_column("t_member", "date_of_birth")
    op.drop_column("t_member", "gender")
    op.drop_column("t_member", "cover_id")
    op.drop_column("t_member", "avatar_id")
    op.drop_column("t_member", "bio")
    op.drop_column("t_member", "username")
