from typing import Any, ClassVar, Dict

from MiravejaCore.Shared.Events.Domain.Models import DomainEvent


class ImageMetadataRegisteredEvent(DomainEvent):
    """Event representing the registration of new image metadata."""

    type: ClassVar[str] = "image.metadata.registered"
    aggregateType: str = "ImageMetadata"
    version: int = 1
    imageMetadataId: str
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
            aggregateId=str(imageMetadata.id),
            imageMetadataId=str(imageMetadata.id),
            data=imageMetadata.model_dump(exclude={"id", "uploadedAt", "updatedAt"}),
        )


class ImageMetadataUpdatedEvent(DomainEvent):
    """Event representing the update of existing image metadata."""

    type: ClassVar[str] = "image.metadata.updated"
    aggregateType: str = "ImageMetadata"
    version: int = 1
    imageMetadataId: str
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
            aggregateId=str(newImageMetadata.id),
            imageMetadataId=str(newImageMetadata.id),
            oldData=oldImageMetadata.model_dump(exclude={"id", "uploadedAt", "updatedAt"}),
            newData=newImageMetadata.model_dump(exclude={"id", "uploadedAt", "updatedAt"}),
        )


class ImageMetadataVectorIdAssignedEvent(DomainEvent):
    """Event representing the assignment of a vector ID to image metadata."""

    type: ClassVar[str] = "image.metadata.vector_id.assigned"
    aggregateType: str = "ImageMetadata"
    version: int = 1
    imageMetadataId: str
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
            aggregateId=str(imageMetadata.id),
            imageMetadataId=str(imageMetadata.id),
            vectorId=str(vectorId.id),
        )


class ImageMetadataVectorIdUnassignedEvent(DomainEvent):
    """Event representing the unassignment of a vector ID from image metadata."""

    type: ClassVar[str] = "image.metadata.vector_id.unassigned"
    aggregateType: str = "ImageMetadata"
    version: int = 1
    imageMetadataId: str
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
            aggregateId=str(imageMetadata.id),
            imageMetadataId=str(imageMetadata.id),
            vectorId=str(vectorId.id),
        )
