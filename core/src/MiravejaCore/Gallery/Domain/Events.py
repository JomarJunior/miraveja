from typing import Any, ClassVar, Dict

from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent
from MiravejaCore.Shared.Events.Domain.Services import eventRegistry


@eventRegistry.RegisterEvent(eventType="image.metadata.registered", eventVersion=1)
class ImageMetadataRegisteredEvent(DomainEvent):
    """Event representing the registration of new image metadata."""

    type: ClassVar[str] = "image.metadata.registered"
    aggregateType: str = "ImageMetadata"
    version: ClassVar[int] = 1
    imageMetadataId: int
    data: Dict[str, Any]

    @classmethod
    def FromModel(cls, imageMetadata) -> "ImageMetadataRegisteredEvent":
        """
        Create an ImageMetadataRegisteredEvent from an ImageMetadata model.

        Args:
            imageMetadata (ImageMetadata): The image metadata model.
        Returns:
            ImageMetadataRegisteredEvent: The created event.
        """
        return cls(
            aggregateId=int(imageMetadata.id),
            imageMetadataId=int(imageMetadata.id),
            data=imageMetadata.model_dump(exclude={"id", "uploadedAt", "updatedAt"}),
        )


@eventRegistry.RegisterEvent(eventType="image.metadata.updated", eventVersion=1)
class ImageMetadataUpdatedEvent(DomainEvent):
    """Event representing the update of existing image metadata."""

    type: ClassVar[str] = "image.metadata.updated"
    aggregateType: str = "ImageMetadata"
    version: ClassVar[int] = 1
    imageMetadataId: int
    oldData: Dict[str, Any]
    newData: Dict[str, Any]

    @classmethod
    def FromModel(cls, oldImageMetadata, newImageMetadata) -> "ImageMetadataUpdatedEvent":
        """
        Create an ImageMetadataUpdatedEvent from an ImageMetadata model.

        Args:
            oldImageMetadata (ImageMetadata): The old image metadata model.
            newImageMetadata (ImageMetadata): The new image metadata model.
        Returns:
            ImageMetadataUpdatedEvent: The created event.
        """
        return cls(
            aggregateId=int(newImageMetadata.id),
            imageMetadataId=int(newImageMetadata.id),
            oldData=oldImageMetadata.model_dump(exclude={"id", "uploadedAt", "updatedAt"}),
            newData=newImageMetadata.model_dump(exclude={"id", "uploadedAt", "updatedAt"}),
        )


@eventRegistry.RegisterEvent(eventType="image.metadata.vector_id.assigned", eventVersion=1)
class ImageMetadataVectorIdAssignedEvent(DomainEvent):
    """Event representing the assignment of a vector ID to image metadata."""

    type: ClassVar[str] = "image.metadata.vector_id.assigned"
    aggregateType: str = "ImageMetadata"
    version: ClassVar[int] = 1
    imageMetadataId: int
    vectorId: str

    @classmethod
    def FromModel(cls, imageMetadata, vectorId) -> "ImageMetadataVectorIdAssignedEvent":
        """
        Create an ImageMetadataVectorIdAssignedEvent from an ImageMetadata model.

        Args:
            imageMetadata (ImageMetadata): The image metadata model.
            vectorId (VectorId): The assigned vector ID.
        """
        return cls(
            aggregateId=int(imageMetadata.id),
            imageMetadataId=int(imageMetadata.id),
            vectorId=str(vectorId.id),
        )


@eventRegistry.RegisterEvent(eventType="image.metadata.vector_id.unassigned", eventVersion=1)
class ImageMetadataVectorIdUnassignedEvent(DomainEvent):
    """Event representing the unassignment of a vector ID from image metadata."""

    type: ClassVar[str] = "image.metadata.vector_id.unassigned"
    aggregateType: str = "ImageMetadata"
    version: ClassVar[int] = 1
    imageMetadataId: int
    vectorId: str

    @classmethod
    def FromModel(cls, imageMetadata, vectorId) -> "ImageMetadataVectorIdUnassignedEvent":
        """
        Create an ImageMetadataVectorIdUnassignedEvent from an ImageMetadata model.

        Args:
            imageMetadata (ImageMetadata): The image metadata model.
            vectorId (VectorId): The unassigned vector ID.
        """
        return cls(
            aggregateId=int(imageMetadata.id),
            imageMetadataId=int(imageMetadata.id),
            vectorId=str(vectorId.id),
        )


@eventRegistry.RegisterEvent(eventType="image.thumbnail.set", eventVersion=1)
class ImageThumbnailSetEvent(DomainEvent):
    """Event representing the generation of an image thumbnail."""

    type: ClassVar[str] = "image.thumbnail.set"
    aggregateType: str = "ImageMetadata"
    version: ClassVar[int] = 1
    imageMetadataId: int
    thumbnailUri: str

    @classmethod
    def FromModel(cls, imageMetadata) -> "ImageThumbnailSetEvent":
        """
        Create an ImageThumbnailSetEvent from an ImageMetadata model.
        Args:
            imageMetadata (ImageMetadata): The image metadata model.
        """
        return cls(
            aggregateId=int(imageMetadata.id),
            imageMetadataId=int(imageMetadata.id),
            thumbnailUri=imageMetadata.thumbnailUri,
        )
