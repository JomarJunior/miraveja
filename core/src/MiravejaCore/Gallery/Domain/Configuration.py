import os

from pydantic import BaseModel, Field

from MiravejaCore.Gallery.Application.GetPresignedPostUrl import MimeType
from MiravejaCore.Gallery.Domain.Models import Size


class GalleryConfig(BaseModel):
    """Configuration specific to the Gallery module."""

    thumbnailSize: Size = Field(
        default=Size(width=150, height=150), description="Default size for generated thumbnails"
    )
    thumbnailFormat: MimeType = Field(
        default=MimeType.JPEG, description="Default image format for generated thumbnails"
    )

    @classmethod
    def FromEnv(cls) -> "GalleryConfig":
        return cls(
            thumbnailSize=Size(
                width=int(os.getenv("GALLERY_THUMBNAIL_WIDTH", "150")),
                height=int(os.getenv("GALLERY_THUMBNAIL_HEIGHT", "150")),
            ),
            thumbnailFormat=MimeType(os.getenv("GALLERY_THUMBNAIL_FORMAT", "image/jpeg")),
        )
