"""Create t_image_metadata, t_generation_metadata, t_lora_metadata, t_lora_meta_to_generation_meta tables and sequences

Revision ID: 9ff1299684b3
Revises: 4be0571e9868
Create Date: 2025-10-08 16:55:20.947802

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "9ff1299684b3"
down_revision: Union[str, Sequence[str], None] = "4be0571e9868"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create enum types for SamplerType and SchedulerType
    sampler_type_enum = postgresql.ENUM(
        "DPMPP_2M",
        "DPMPP_SDE",
        "DPMPP_2M_SDE",
        "DPMPP_2M_SDE_HEUN",
        "DPMPP_2S_A",
        "DPMPP_3M_SDE",
        "EULER_A",
        "EULER",
        "LMS",
        "HEUN",
        "DPM2",
        "DPM2_A",
        "DPM_FAST",
        "DPM_ADAPTIVE",
        "RESTART",
        "HEUNPP2",
        "IPNDM",
        "IPNDM_V",
        "DEIS",
        "DDIM",
        "DDIM_CFGPP",
        "PLMS",
        "UNIPC",
        "LCM",
        "DDPM",
        "OTHER",
        name="samplertype",
    )

    scheduler_type_enum = postgresql.ENUM(
        "AUTOMATIC",
        "UNIFORM",
        "KARRAS",
        "EXPONENTIAL",
        "POLYEXPONENTIAL",
        "SGM_UNIFORM",
        "KL_OPTIMAL",
        "ALIGN_YOUR_STEPS",
        "SIMPLE",
        "NORMAL",
        "DDIM",
        "BETA",
        "TURBO",
        "ALIGN_YOUR_STEPS_GITS",
        "ALIGN_YOUR_STEPS_11",
        "ALIGN_YOUR_STEPS_32",
        name="schedulertype",
    )

    # Create enums only if they don't exist
    connection = op.get_bind()
    sampler_type_enum.create(connection, checkfirst=True)
    scheduler_type_enum.create(connection, checkfirst=True)

    # Create t_image_metadata table
    op.create_table(
        "t_image_metadata",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ownerId", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("subtitle", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=True),
        sa.Column("width", sa.Integer(), nullable=False),
        sa.Column("height", sa.Integer(), nullable=False),
        sa.Column("repositoryType", sa.String(length=50), nullable=False),
        sa.Column("uri", sa.String(length=500), nullable=False),
        sa.Column("isAiGenerated", sa.Boolean(), nullable=False, default=False),
        sa.Column("vectorId", sa.Integer(), nullable=True),
        sa.Column("uploadedAt", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updatedAt", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uri"),  # Ensures unique URIs to prevent duplicate images
        sa.ForeignKeyConstraint(["ownerId"], ["t_member.id"]),
    )

    # Create t_generation_metadata table
    op.create_table(
        "t_generation_metadata",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("imageId", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.String(length=2000), nullable=False),
        sa.Column("negativePrompt", sa.String(length=2000), nullable=True),
        sa.Column("seed", sa.String(), nullable=True),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("sampler", postgresql.ENUM(name="samplertype", create_type=False), nullable=True),
        sa.Column("scheduler", postgresql.ENUM(name="schedulertype", create_type=False), nullable=True),
        sa.Column("steps", sa.Integer(), nullable=True),
        sa.Column("cfgScale", sa.Float(), nullable=True),
        sa.Column("size", sa.String(length=20), nullable=True),
        sa.Column("techniques", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["imageId"],
            ["t_image_metadata.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("imageId"),  # Ensures one-to-one relationship
    )

    # Create t_lora_metadata table
    op.create_table(
        "t_lora_metadata",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hash", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hash"),  # Ensures unique LoRA hashes
    )

    # Create junction table for many-to-many relationship
    op.create_table(
        "t_lora_meta_to_generation_meta",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("loraId", sa.Integer(), nullable=False),
        sa.Column("generationMetadataId", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["generationMetadataId"],
            ["t_generation_metadata.id"],
        ),
        sa.ForeignKeyConstraint(
            ["loraId"],
            ["t_lora_metadata.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("loraId", "generationMetadataId"),  # Prevents duplicate LoRA-Generation relationships
    )

    # Create indexes for better query performance
    op.create_index("ix_t_image_metadata_ownerId", "t_image_metadata", ["ownerId"])
    op.create_index("ix_t_image_metadata_uri", "t_image_metadata", ["uri"])  # For FindByUri queries
    op.create_index("ix_t_image_metadata_isAiGenerated", "t_image_metadata", ["isAiGenerated"])
    op.create_index("ix_t_image_metadata_uploadedAt", "t_image_metadata", ["uploadedAt"])
    op.create_index("ix_t_generation_metadata_imageId", "t_generation_metadata", ["imageId"])
    op.create_index("ix_t_lora_metadata_hash", "t_lora_metadata", ["hash"])
    op.create_index("ix_t_lora_meta_to_generation_meta_loraId", "t_lora_meta_to_generation_meta", ["loraId"])
    op.create_index(
        "ix_t_lora_meta_to_generation_meta_generationMetadataId",
        "t_lora_meta_to_generation_meta",
        ["generationMetadataId"],
    )

    # Create sequences for all ID generation
    op.execute("CREATE SEQUENCE IF NOT EXISTS seq_image_metadata_id START 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS seq_generation_metadata_id START 1")
    op.execute("CREATE SEQUENCE IF NOT EXISTS seq_lora_metadata_id START 1")


def downgrade() -> None:
    """Downgrade schema."""
    # Drop sequences
    op.execute("DROP SEQUENCE IF EXISTS seq_lora_metadata_id")
    op.execute("DROP SEQUENCE IF EXISTS seq_generation_metadata_id")
    op.execute("DROP SEQUENCE IF EXISTS seq_image_metadata_id")

    # Drop indexes
    op.drop_index("ix_t_lora_meta_to_generation_meta_generationMetadataId", table_name="t_lora_meta_to_generation_meta")
    op.drop_index("ix_t_lora_meta_to_generation_meta_loraId", table_name="t_lora_meta_to_generation_meta")
    op.drop_index("ix_t_lora_metadata_hash", table_name="t_lora_metadata")
    # op.drop_index("ix_t_generation_metadata_imageId", table_name="t_generation_metadata")
    op.drop_index("ix_t_image_metadata_uploadedAt", table_name="t_image_metadata")
    op.drop_index("ix_t_image_metadata_isAiGenerated", table_name="t_image_metadata")
    op.drop_index("ix_t_image_metadata_uri", table_name="t_image_metadata")
    op.drop_index("ix_t_image_metadata_ownerId", table_name="t_image_metadata")

    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table("t_lora_meta_to_generation_meta")
    op.drop_table("t_lora_metadata")
    op.drop_table("t_generation_metadata")
    op.drop_table("t_image_metadata")

    # Drop enum types
    postgresql.ENUM(name="schedulertype").drop(op.get_bind())
    postgresql.ENUM(name="samplertype").drop(op.get_bind())
