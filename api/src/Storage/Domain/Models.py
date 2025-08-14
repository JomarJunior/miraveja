"""
Storage models.
"""

from src.Core.Events.Bus import EventEmitter
from src.Storage.Domain.Enums import ImageFormatEnum
from src.Storage.Domain.Events import (
    ImageRegisteredEvent,
    ImageUpdatedEvent,
    ProviderRegisteredEvent,
    ProviderUpdatedEvent,
    ImageContentDownloadedEvent,
    ImageContentUploadedEvent
)
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
import base64
import copy

Base = declarative_base(cls=EventEmitter)

class Image(Base):
    __tablename__ = "t_images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uri: Mapped[str] = mapped_column(sa.String(length=255), nullable=False)
    image_metadata: Mapped[dict] = mapped_column(sa.JSON, nullable=False)
    provider_id: Mapped[int] = mapped_column(sa.ForeignKey("t_providers.id"), nullable=False)

    @staticmethod
    def create(uri: str, image_metadata: dict, provider_id: int) -> "Image":
        image: Image = Image(
            uri=uri,
            image_metadata=image_metadata,
            provider_id=provider_id
        )
        image.emit_event(ImageRegisteredEvent(image))

        return image

    def change(self, uri: str, image_metadata: dict, provider_id: int) -> None:
        # Create a copy
        old_image = copy.deepcopy(self)
        
        self.uri = uri
        self.image_metadata = image_metadata
        self.provider_id = provider_id

        # Emit the event with the new and the old image
        self.emit_event(ImageUpdatedEvent(self, old_image))

    @staticmethod
    def from_dict(data: dict) -> "Image":
        id = data.get("id")
        uri = data["uri"]
        image_metadata = data["image_metadata"]
        provider_id = data["provider_id"]

        if id is None:
            raise ValueError("Missing 'id' field")
        if uri is None:
            raise ValueError("Missing 'uri' field")
        if image_metadata is None:
            raise ValueError("Missing 'image_metadata' field")
        if provider_id is None:
            raise ValueError("Missing 'provider_id' field")

        return Image(
            id=id,
            uri=uri,
            image_metadata=image_metadata,
            provider_id=provider_id
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "uri": self.uri,
            "image_metadata": self.image_metadata,
            "provider_id": self.provider_id
        }
    
class Provider(Base):
    __tablename__ = "t_providers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sa.String(length=100), nullable=False)

    @staticmethod
    def create(name: str) -> "Provider":
        provider: Provider = Provider(
            name=name
        )
        provider.emit_event(ProviderRegisteredEvent(provider))
        return provider

    def change(self, name: str) -> None:
        # Create a copy
        old_provider = copy.deepcopy(self)

        # Update the fields
        self.name = name

        # Emit the event with the new and the old provider
        self.emit_event(ProviderUpdatedEvent(self, old_provider))

    @staticmethod
    def from_dict(data: dict) -> "Provider":
        id = data.get("id")
        name = data["name"]

        if id is None:
            raise ValueError("Missing 'id' field")
        if name is None:
            raise ValueError("Missing 'name' field")

        return Provider(
            id=id,
            name=name
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name
        }

class ImageContent(EventEmitter):
    """
    This class is not stored in the database. It will use the filesystem instead.
    It stores the content of the image in Base64 with the type prefix.
    Example:
        PNG -> data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
        JPG -> data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASAB...
    """
    def __init__(self, uri: str, content: str):
        super().__init__()
        self.uri = uri
        self.content = content

    def get_format(self) -> ImageFormatEnum:
        starts_with: str = self.content.split(";")[0]
        if (starts_with not in ImageFormatEnum.__members__.values()):
            raise ValueError("Unknown image format: " + starts_with)
        return ImageFormatEnum(starts_with)

    def get_bytes_content(self) -> bytes:
        header, encoded = self.content.split(",", 1)
        
        self.emit_event(ImageContentDownloadedEvent(self))

        return base64.b64decode(encoded)

    def to_dict(self) -> dict:
        return {
            "uri": self.uri,
            "content": self.content
        }

    @classmethod
    def create(cls, uri: str, content: str) -> "ImageContent":
        image_content: ImageContent = ImageContent(
            uri=uri,
            content=content
        )

        image_content.emit_event(ImageContentUploadedEvent(image_content))

        return image_content

    @classmethod
    def from_dict(cls, data: dict) -> "ImageContent":
        return cls(
            uri=data["uri"],
            content=data["content"]
        )

    @classmethod
    def from_uri_format_and_bytes(cls, uri: str, format: ImageFormatEnum, content: bytes) -> "ImageContent":
        encoded = base64.b64encode(content).decode("utf-8")
        return cls(
            uri=uri,
            content=f"{format};base64,{encoded}"
        )
