import uuid
import os
from typing import Any, Dict
from urllib.parse import urlparse
from datetime import datetime, timezone
from PIL import Image

from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Shared.Storage.Domain.Enums import MimeType
from MiravejaCore.Shared.Storage.Domain.Exceptions import (
    ImageContentTooLargeException,
    ImageNotValidException,
    UnsupportedImageMimeTypeException,
)
from MiravejaCore.Shared.Storage.Domain.Models import ImageContent


class ImageValidationService:
    def __init__(self, config: MinIoConfig):
        self.config = config

    def ValidateImageMimeType(self, mimeType: MimeType) -> None:
        """Validate the image MIME type against the allowed types."""
        if mimeType not in self.config.allowedMimeTypes:
            raise UnsupportedImageMimeTypeException(mimeType)

    def ValidateImageSize(self, image: ImageContent) -> None:
        """Validate the image size against the maximum allowed size."""
        if image.sizeBytes > self.config.maxFileSizeBytes:
            raise ImageContentTooLargeException(
                self.config.maxFileSizeBytes,
                image.sizeBytes,
            )

    def ValidateIsImage(self, image: ImageContent) -> None:
        """Validate that the binary content is a valid image."""
        try:
            image.binary.seek(0)  # Reset stream position before opening
            img = Image.open(image.binary)
            img.verify()  # Verify that it is, in fact, an image
            image.binary.seek(0)  # Reset stream position after verification
        except (IOError, SyntaxError) as e:
            raise ImageNotValidException() from e

    def ValidateImageContent(self, image: ImageContent) -> None:
        """
        Validate the image content for predefined constraints.
        """
        self.ValidateImageMimeType(image.mimeType)
        self.ValidateImageSize(image)
        self.ValidateIsImage(image)


class ImagePathService:
    @staticmethod
    def GenerateUniqueImagePath(ownerId: MemberId, image: ImageContent) -> str:
        """
        Generate a unique path for storing the image.
        The path format is: members/{ownerId}/images/{year}/{month}/{uuid}{extension}
        """

        # Generate a unique identifier for the image
        uniqueId = str(uuid.uuid4())

        # Get the current date to organize images by date
        currentDate = datetime.now(timezone.utc)
        year = f"{currentDate.year:04d}"
        month = f"{currentDate.month:02d}"

        # Get the file extension
        extension = image.extension

        # Construct the unique image path
        imagePath = os.path.join(
            "members",
            ownerId.id,
            "images",
            year,
            month,
            f"{uniqueId}{extension}",
        )

        return imagePath


class ImageMetadataService:
    @staticmethod
    def PrepareImageMetadata(image: ImageContent) -> Dict[str, Any]:
        """
        Prepare metadata for the image to be stored alongside the binary content.
        """
        metadata = {
            "ownerId": image.ownerId.id,
            "originalFilename": image.filename,
            "mimeType": image.mimeType,
            "sizeBytes": str(image.sizeBytes),  # Store size as string for metadata
            "uploadedAt": datetime.now(timezone.utc).isoformat(),
        }
        return metadata


class SignedUrlService:
    def __init__(self, config: MinIoConfig):
        self.config = config

    def GetRelativeUrl(self, fullUrl: str) -> str:
        """
        Extract the relative URL from a full presigned URL.
        """

        parsedUrl = urlparse(fullUrl)

        relativeUrl = parsedUrl.path.lstrip("/")
        return f"{self.config.outsideEndpoint}{relativeUrl}"
