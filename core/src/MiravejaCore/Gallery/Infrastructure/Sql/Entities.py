from datetime import datetime
from typing import Any, Dict, List, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from MiravejaCore.Gallery.Domain.Enums import SamplerType, SchedulerType
from MiravejaCore.Gallery.Domain.Models import GenerationMetadata, ImageMetadata, LoraMetadata

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

    @classmethod
    def FromDomain(cls, domainLoraMetadata: LoraMetadata) -> "LoraMetadataEntity":
        return cls(
            id=domainLoraMetadata.id.id,
            hash=domainLoraMetadata.hash,
            name=domainLoraMetadata.name,
        )


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

    @classmethod
    def FromDomain(cls, domainGenerationMetadata: GenerationMetadata) -> "GenerationMetadataEntity":
        loraEntities = (
            [LoraMetadataEntity.FromDomain(lora) for lora in domainGenerationMetadata.loras]
            if domainGenerationMetadata.loras
            else []
        )

        techniquesStr = ",".join(domainGenerationMetadata.techniques) if domainGenerationMetadata.techniques else None

        return cls(
            id=domainGenerationMetadata.id.id,
            imageId=domainGenerationMetadata.imageId.id,
            prompt=domainGenerationMetadata.prompt,
            negativePrompt=domainGenerationMetadata.negativePrompt,
            seed=domainGenerationMetadata.seed,
            model=domainGenerationMetadata.model,
            sampler=domainGenerationMetadata.sampler,
            scheduler=domainGenerationMetadata.scheduler,
            steps=domainGenerationMetadata.steps,
            cfgScale=domainGenerationMetadata.cfgScale,
            size=str(domainGenerationMetadata.size) if domainGenerationMetadata.size else None,
            loras=loraEntities,
            techniques=techniquesStr,
        )


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
    thumbnailUri: Mapped[Optional[str]] = mapped_column(sa.String(500), nullable=True)
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
            "thumbnailUri": self.thumbnailUri,
            "isAiGenerated": self.isAiGenerated,
            "generationMetadata": self.generationMetadata.ToDict() if self.generationMetadata else None,
            "vectorId": self.vectorId,
            "uploadedAt": self.uploadedAt,
            "updatedAt": self.updatedAt,
        }

    @classmethod
    def FromDomain(cls, domainImageMetadata: ImageMetadata) -> "ImageMetadataEntity":
        return cls(
            id=domainImageMetadata.id.id,
            ownerId=domainImageMetadata.ownerId.id,
            title=domainImageMetadata.title,
            subtitle=domainImageMetadata.subtitle,
            description=domainImageMetadata.description,
            width=domainImageMetadata.size.width,
            height=domainImageMetadata.size.height,
            repositoryType=domainImageMetadata.repositoryType.value,
            uri=domainImageMetadata.uri,
            thumbnailUri=domainImageMetadata.thumbnailUri,
            isAiGenerated=domainImageMetadata.isAiGenerated,
            vectorId=domainImageMetadata.vectorId.id if domainImageMetadata.vectorId else None,
            uploadedAt=domainImageMetadata.uploadedAt,
            updatedAt=domainImageMetadata.updatedAt,
        )
