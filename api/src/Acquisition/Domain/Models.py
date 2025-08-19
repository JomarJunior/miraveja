"""
Image Acquisition models
"""

from src.Acquisition.Domain.Events import ImageCreatedEvent, ImageDownloadedEvent
from src.Core.Events.Bus import EventEmitter
from pydantic import BaseModel, Field

class Provider(BaseModel):
    """
    Represents a data provider in the acquisition domain.
    This model stores information about providers that supply images to the system.
    Each provider can have multiple associated images through a one-to-many relationship.
    Attributes:
        id (int): Primary key identifier for the provider.
        name (str): Name of the provider (max 255 characters).
    """
    id: int = Field(..., description="The unique identifier for the provider")
    name: str = Field(..., description="The name of the provider")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }

    @classmethod
    def from_dict(cls, data: dict):
        id = data.get("id")
        if not id:
            raise ValueError("Missing 'id' field")

        name = data.get("name")
        if not name:
            raise ValueError("Missing 'name' field")

        return cls(
            id=id,
            name=name
        )

class Image(BaseModel, EventEmitter):
    """
    Represents an image DTO in the acquisition domain.
    This model stores image data including URI location, metadata, and
    associated provider information. Images are linked to providers through
    a foreign key relationship.
    Attributes:
        uri (str): URI location of the image file (max 255 characters).
        metadata (dict): JSON metadata associated with the image.
        provider_id (int): Foreign key reference to the associated provider.
    """
    uri: str = Field(..., description="The URI location of the image")
    metadata: dict = Field(..., description="The metadata associated with the image")
    provider_id: int = Field(..., description="The ID of the associated provider")

    @staticmethod
    def create(uri: str, metadata: dict, provider_id: int):
        image = Image(
            uri=uri,
            metadata=metadata,
            provider_id=provider_id
        )
        image.emit_event(ImageCreatedEvent(image))
        return image

    def to_dict(self):
        return {
            "uri": self.uri,
            "metadata": self.metadata,
            "provider_id": self.provider_id
        }

    @classmethod
    def from_dict(cls, data: dict):
        uri = data.get("uri")
        if not uri:
            raise ValueError("Missing 'uri' field")

        metadata = data.get("metadata")
        if not metadata:
            raise ValueError("Missing 'metadata' field")

        provider_id = data.get("provider_id")
        if not provider_id:
            raise ValueError("Missing 'provider_id' field")

        return cls(
            uri=uri,
            metadata=metadata,
            provider_id=provider_id
        )

class ImageContent(BaseModel, EventEmitter):
    """
    Represents image content with URI and base64-encoded data.
    This model encapsulates image information including its URI location and
    the actual image data encoded in base64 format.
    Attributes:
        uri (str): The URI of the image location.
        base64_content (str): The base64-encoded content of the image.
    Methods:
        to_dict(): Converts the ImageContent instance to a dictionary representation.
        from_dict(data): Class method to create an ImageContent instance from a dictionary.
    Raises:
        ValueError: When required fields 'uri' or 'base64_content' are missing in from_dict().
    Example:
        >>> image_content = ImageContent(
        ...     uri="https://example.com/image.jpg",
        ...     base64_content="iVBORw0KGgoAAAANSUhEUgAA..."
        ... )
        >>> image_dict = image_content.to_dict()
        >>> restored_image = ImageContent.from_dict(image_dict)
    """

    uri: str = Field(..., description="The URI of the image")
    base64_content: str = Field(..., description="The base64-encoded content of the image")

    @staticmethod
    def create(uri: str, base64_content: str):
        content = ImageContent(
            uri=uri,
            base64_content=base64_content
        )
        content.emit_event(ImageDownloadedEvent(content))
        return content

    def to_dict(self):
        return {
            "uri": self.uri,
            "base64_content": self.base64_content
        }

    @classmethod
    def from_dict(cls, data: dict):
        uri = data.get("uri")
        if not uri:
            raise ValueError("Missing 'uri' field")

        base64_content = data.get("base64_content")
        if not base64_content:
            raise ValueError("Missing 'base64_content' field")

        return cls(
            uri=uri,
            base64_content=base64_content
        )
