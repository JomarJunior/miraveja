from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_serializer, field_validator, model_serializer, model_validator

from Miraveja.Gallery.Domain.Enums import ImageRepositoryType, SamplerType, SchedulerType, TechniqueType
from Miraveja.Gallery.Domain.Events import (
    ImageMetadataRegisteredEvent,
    ImageMetadataUpdatedEvent,
    ImageMetadataVectorIdAssignedEvent,
    ImageMetadataVectorIdUnassignedEvent,
)
from Miraveja.Gallery.Domain.Exceptions import MalformedImageSizeStringException
from Miraveja.Shared.Events.Domain.Models import EventEmitter
from Miraveja.Shared.Identifiers.Models import GenerationMetadataId, ImageMetadataId, LoraMetadataId, MemberId, VectorId


class Size(BaseModel):
    """Model representing the dimensions of an image."""

    width: int = Field(..., description="Width of the image in pixels", gt=0)
    height: int = Field(..., description="Height of the image in pixels", gt=0)

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"

    @model_validator(mode="before")
    def NormalizeStringInput(cls, values: Any) -> Any:
        """Allow initialization from a string formatted as 'WIDTHxHEIGHT'."""
        if isinstance(values, str):
            return cls.CreateFromString(values).model_dump()
        return values

    @classmethod
    def CreateFromString(cls, sizeStr: str) -> "Size":
        """Create a Size instance from a string formatted as 'WIDTHxHEIGHT'."""
        try:
            widthStr, heightStr = sizeStr.lower().split("x")
            width = int(widthStr)
            height = int(heightStr)
            return cls(width=width, height=height)
        except (ValueError, AttributeError) as exception:
            raise MalformedImageSizeStringException(sizeStr) from exception

    @property
    def aspectRatio(self) -> float:
        """Calculate and return the aspect ratio (width / height) of the size."""
        return self.width / self.height

    @property
    def megaPixels(self) -> float:
        """Calculate and return the size in megapixels."""
        return (self.width * self.height) / 1_000_000

    def IsLandscape(self) -> bool:
        """Determine if the size is in landscape orientation."""
        return self.width > self.height

    def IsPortrait(self) -> bool:
        """Determine if the size is in portrait orientation."""
        return self.height > self.width

    def IsSquare(self) -> bool:
        """Determine if the size is square."""
        return self.width == self.height


class LoraMetadata(BaseModel):
    """Model representing metadata for a LoRA (Low-Rank Adaptation) used in image generation."""

    id: LoraMetadataId = Field(..., description="Unique identifier for the LoRA")
    hash: str = Field(..., description="Hash of the LoRA", min_length=1, max_length=255)
    name: Optional[str] = Field(None, description="Name of the LoRA", min_length=1, max_length=255)
    generationMetadatas: Optional[List[GenerationMetadataId]] = Field(
        None, description="List of generation metadata IDs that used this LoRA"
    )

    @model_serializer
    def SerializeModel(self) -> dict:
        return {
            "id": int(self.id),
            "hash": self.hash,
            "name": self.name,
        }

    @classmethod
    def Register(cls, id: LoraMetadataId, hash: str, name: Optional[str] = None) -> "LoraMetadata":
        """Factory method to create a new LoraMetadata instance."""
        return cls(id=id, hash=hash, name=name, generationMetadatas=[])


class GenerationMetadata(BaseModel):
    """Model representing metadata for a generation process. Not possible to update after creation."""

    id: GenerationMetadataId = Field(..., description="Unique identifier for the generation metadata")
    imageId: ImageMetadataId = Field(..., description="Identifier linking to the associated image")
    prompt: str = Field(..., description="The prompt used for generation", max_length=2000, min_length=1)
    negativePrompt: Optional[str] = Field(None, description="The negative prompt used for generation", max_length=2000)
    seed: Optional[str] = Field(None, description="The seed used for generation")
    model: Optional[str] = Field(None, description="The hash of the model used for generation")
    sampler: Optional[SamplerType] = Field(None, description="The sampler used for generation")
    scheduler: Optional[SchedulerType] = Field(None, description="The scheduler used for generation")
    steps: Optional[int] = Field(None, description="The number of steps used for generation")
    cfgScale: Optional[float] = Field(None, description="The CFG scale used for generation")
    size: Optional[Size] = Field(None, description="The size used for generation")
    loras: Optional[List[LoraMetadata]] = Field(None, description="List of LoRAs used for generation")
    techniques: Optional[List[TechniqueType]] = Field(None, description="List of techniques used for generation")

    @field_validator("cfgScale")
    @classmethod
    def ValidateCfgScale(cls, value: Optional[float]) -> Optional[float]:
        """Validate that cfgScale, if provided, is within the range 1.0 to 30.0."""
        if value is not None and not 1.0 <= value <= 30.0:
            raise ValueError("cfgScale must be between 1.0 and 30.0.")
        return value

    @field_serializer("techniques")
    def SerializeTechniques(self, value: Optional[List[TechniqueType]]) -> Optional[str]:
        """Serialize techniques list to a comma-separated string."""
        if value is None:
            return None
        return ",".join(value)

    @field_serializer("size")
    def SerializeSize(self, value: Optional[Size]) -> Optional[str]:
        """Serialize Size to a string formatted as 'WIDTHxHEIGHT'."""
        if value is None:
            return None
        return str(value)

    @classmethod
    def Register(
        cls,
        id: GenerationMetadataId,
        imageId: ImageMetadataId,
        prompt: str,
        negativePrompt: Optional[str] = None,
        seed: Optional[str] = None,
        model: Optional[str] = None,
        sampler: Optional[SamplerType] = None,
        scheduler: Optional[SchedulerType] = None,
        steps: Optional[int] = None,
        cfgScale: Optional[float] = None,
        size: Optional[Size] = None,
        loras: Optional[List[LoraMetadata]] = None,
        techniques: Optional[List[TechniqueType]] = None,
    ) -> "GenerationMetadata":
        """Factory method to create a new GenerationMetadata instance."""
        return cls(
            id=id,
            imageId=imageId,
            prompt=prompt,
            negativePrompt=negativePrompt,
            seed=seed,
            model=model,
            sampler=sampler,
            scheduler=scheduler,
            steps=steps,
            cfgScale=cfgScale,
            size=size,
            loras=loras,
            techniques=techniques,
        )


class ImageMetadata(EventEmitter):
    """Model representing metadata for an image in the gallery."""

    id: ImageMetadataId = Field(..., description="Unique identifier for the image metadata")
    ownerId: MemberId = Field(..., description="Identifier of the member who owns the image")

    # Descriptive details
    title: str = Field(..., description="Title of the image", min_length=1, max_length=200)
    subtitle: str = Field(..., description="Subtitle of the image", min_length=0, max_length=200)
    description: Optional[str] = Field(None, description="Description of the image", min_length=0, max_length=2000)
    size: Size = Field(..., description="Dimensions of the image")

    # Location details
    repositoryType: ImageRepositoryType = Field(..., description="The repository type where the image is stored")
    uri: str = Field(
        ..., description="The Uniform Resource Identifier (URI) of the image", min_length=1, max_length=500
    )

    # AI generation details
    isAiGenerated: bool = Field(..., description="Flag indicating if the image was AI-generated")
    generationMetadata: Optional[GenerationMetadata] = Field(
        None, description="Metadata related to the image generation process"
    )

    # Semantic vector data
    vectorId: Optional[VectorId] = Field(None, description="Identifier linking to the associated vector data")

    # Timestamps
    uploadedAt: datetime = Field(
        description="Timestamp when the image was uploaded", default_factory=lambda: datetime.now(timezone.utc)
    )
    updatedAt: datetime = Field(
        description="Timestamp when the image metadata was last updated",
        default_factory=lambda: datetime.now(timezone.utc),
    )

    @field_validator("uploadedAt", "updatedAt")
    @classmethod
    def ValidateTimestamps(cls, value: datetime) -> datetime:
        """Validate that timestamps are not set in the future."""
        now: datetime = datetime.now(timezone.utc)
        if value > now:
            raise ValueError("Timestamp cannot be in the future.")
        return value

    @model_serializer
    def SerializeModel(self) -> dict:
        """
        Custom serializer to convert model to dict
        It converts Size to width and height fields
        """
        return {
            "id": int(self.id),
            "ownerId": str(self.ownerId),
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "width": self.size.width,
            "height": self.size.height,
            "repositoryType": self.repositoryType,
            "uri": self.uri,
            "isAiGenerated": self.isAiGenerated,
            "generationMetadata": self.generationMetadata.model_dump() if self.generationMetadata else None,
            "vectorId": int(self.vectorId) if self.vectorId else None,
            "uploadedAt": self.uploadedAt.isoformat(),
            "updatedAt": self.updatedAt.isoformat(),
        }

    @classmethod
    def Register(
        cls,
        id: ImageMetadataId,
        ownerId: MemberId,
        title: str,
        subtitle: str,
        description: Optional[str],
        size: Size,
        repositoryType: ImageRepositoryType,
        uri: str,
        isAiGenerated: bool,
        generationMetadata: Optional[GenerationMetadata] = None,
        vectorId: Optional[VectorId] = None,
    ) -> "ImageMetadata":
        """Factory method to create a new ImageMetadata instance."""
        imageMetadata = cls(
            id=id,
            ownerId=ownerId,
            title=title,
            subtitle=subtitle,
            description=description,
            size=size,
            repositoryType=repositoryType,
            uri=uri,
            isAiGenerated=isAiGenerated,
            generationMetadata=generationMetadata,
            vectorId=vectorId,
        )

        imageMetadata.EmitEvent(ImageMetadataRegisteredEvent.FromModel(imageMetadata))

        return imageMetadata

    def IsAiGeneratedWithMetadata(self) -> bool:
        """Check if the image is AI-generated and has associated generation metadata."""
        return self.isAiGenerated and self.generationMetadata is not None

    def HasVectorData(self) -> bool:
        """Check if the image has associated vector data."""
        return self.vectorId is not None

    def GetDisplayName(self) -> str:
        """Get a display name combining title and subtitle."""
        return f"{self.title} - {self.subtitle}"

    def Update(self, title: str, subtitle: str, description: Optional[str]) -> None:
        """Update the title, subtitle, and description of the image if changed."""
        oldModel = self.model_copy()

        hasChanged = self.title != title or self.subtitle != subtitle or self.description != description

        if not hasChanged:
            return

        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.updatedAt = datetime.now(timezone.utc)

        self.EmitEvent(ImageMetadataUpdatedEvent.FromModel(oldModel, self))

    def AssignVectorId(self, vectorId: VectorId) -> None:
        """Assign a vector ID to the image."""
        self.vectorId = vectorId
        self.updatedAt = datetime.now(timezone.utc)

        self.EmitEvent(ImageMetadataVectorIdAssignedEvent.FromModel(self, vectorId))

    def UnassignVectorId(self) -> None:
        """Unassign the vector ID from the image."""
        oldVectorId = self.vectorId
        self.vectorId = None
        self.updatedAt = datetime.now(timezone.utc)

        self.EmitEvent(ImageMetadataVectorIdUnassignedEvent.FromModel(self, oldVectorId))
