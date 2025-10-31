from datetime import datetime
from typing import Any, Optional, Dict, List
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
import sqlalchemy as sa

from Miraveja.Gallery.Domain.Enums import SamplerType, SchedulerType

Base = declarative_base()


class LoraMetaToGenerationMetaEntity(Base):
    __tablename__ = "t_lora_meta_to_generation_meta"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    loraId: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("t_lora_metadata.id"), nullable=False)
    generationMetadataId: Mapped[int] = mapped_column(
        sa.Integer, sa.ForeignKey("t_generation_metadata.id"), nullable=False
    )

    def ToDict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "loraId": self.loraId,
            "generationMetadataId": self.generationMetadataId,
        }


class LoraMetadataEntity(Base):
    __tablename__ = "t_lora_metadata"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    hash: Mapped[str] = mapped_column(sa.String(255), nullable=False, unique=True)
    name: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)

    # Relationship to generation metadata through junction table
    generationMetadatas: Mapped[List["GenerationMetadataEntity"]] = relationship(
        "GenerationMetadataEntity",
        secondary="t_lora_meta_to_generation_meta",
        back_populates="loras",
    )

    def ToDict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "hash": self.hash,
            "name": self.name,
            "generationMetadatas": [gm.id for gm in self.generationMetadatas] if self.generationMetadatas else [],
        }


class GenerationMetadataEntity(Base):
    __tablename__ = "t_generation_metadata"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    imageId: Mapped[int] = mapped_column(sa.Integer, sa.ForeignKey("t_image_metadata.id"), nullable=False, unique=True)
    prompt: Mapped[str] = mapped_column(sa.String(2000), nullable=False)
    negativePrompt: Mapped[Optional[str]] = mapped_column(sa.String(2000), nullable=True)
    seed: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)
    sampler: Mapped[Optional[SamplerType]] = mapped_column(sa.Enum(SamplerType), nullable=True)
    scheduler: Mapped[Optional[SchedulerType]] = mapped_column(sa.Enum(SchedulerType), nullable=True)
    steps: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)
    cfgScale: Mapped[Optional[float]] = mapped_column(sa.Float, nullable=True)
    size: Mapped[Optional[str]] = mapped_column(sa.String(20), nullable=True)  # Stored as "WIDTHxHEIGHT"
    techniques: Mapped[Optional[str]] = mapped_column(sa.String(255), nullable=True)  # Comma-separated list

    # Many-to-many relationship with LoRA metadata
    loras: Mapped[List["LoraMetadataEntity"]] = relationship(
        "LoraMetadataEntity",
        secondary="t_lora_meta_to_generation_meta",
        back_populates="generationMetadatas",
    )

    # One-to-one relationship with image metadata
    image: Mapped["ImageMetadataEntity"] = relationship(
        "ImageMetadataEntity", back_populates="generationMetadata", uselist=False
    )

    def ToDict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "imageId": self.imageId,
            "prompt": self.prompt,
            "negativePrompt": self.negativePrompt,
            "seed": self.seed,
            "model": self.model,
            "sampler": self.sampler,
            "scheduler": self.scheduler,
            "steps": self.steps,
            "cfgScale": self.cfgScale,
            "size": self.size,
            "loras": [lora.ToDict() for lora in self.loras] if self.loras else [],  # Return list of LoRA dicts
            "techniques": self.techniques.split(",") if self.techniques else None,
        }


class ImageMetadataEntity(Base):
    __tablename__ = "t_image_metadata"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    ownerId: Mapped[str] = mapped_column(sa.String(36), nullable=False)  # Assuming UUID string
    title: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    subtitle: Mapped[str] = mapped_column(sa.String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(sa.String(2000), nullable=True)
    width: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    height: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    repositoryType: Mapped[str] = mapped_column(sa.String(50), nullable=False)  # Enum as string
    uri: Mapped[str] = mapped_column(sa.String(500), nullable=False)
    isAiGenerated: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    vectorId: Mapped[Optional[int]] = mapped_column(sa.Integer, nullable=True)
    uploadedAt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False
    )
    updatedAt: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, onupdate=sa.text("now()")
    )

    # One-to-one relationship with generation metadata
    generationMetadata: Mapped[Optional["GenerationMetadataEntity"]] = relationship(
        "GenerationMetadataEntity", back_populates="image", uselist=False
    )

    def ToDict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "ownerId": self.ownerId,
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "size": {"width": self.width, "height": self.height},
            "repositoryType": self.repositoryType,
            "uri": self.uri,
            "isAiGenerated": self.isAiGenerated,
            "generationMetadata": self.generationMetadata.ToDict() if self.generationMetadata else None,
            "vectorId": self.vectorId,
            "uploadedAt": self.uploadedAt,
            "updatedAt": self.updatedAt,
        }
