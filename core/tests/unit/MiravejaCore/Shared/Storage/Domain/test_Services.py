"""
Unit tests for Storage Domain Services.

Tests ImageValidationService, ImagePathService, ImageMetadataService, and SignedUrlService.
"""

import io
import os
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
import pytest
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
from MiravejaCore.Shared.Storage.Domain.Services import (
    ImageValidationService,
    ImagePathService,
    ImageMetadataService,
    SignedUrlService,
)


class TestImageValidationService:
    """Tests for ImageValidationService."""

    def test_ValidateImageMimeType_WithValidMimeType_ShouldPass(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.allowedMimeTypes = [MimeType.JPEG, MimeType.PNG]
        service = ImageValidationService(config)

        # Act & Assert - should not raise
        service.ValidateImageMimeType(MimeType.JPEG)

    def test_ValidateImageMimeType_WithInvalidMimeType_ShouldRaiseException(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.allowedMimeTypes = [MimeType.JPEG, MimeType.PNG]
        service = ImageValidationService(config)

        # Act & Assert
        with pytest.raises(UnsupportedImageMimeTypeException):
            service.ValidateImageMimeType(MimeType.WEBP)

    def test_ValidateImageSize_WithValidSize_ShouldPass(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.maxFileSizeBytes = 10_000_000  # 10 MB
        service = ImageValidationService(config)

        # Create a small image content
        imageData = b"small image content"
        binary = io.BytesIO(imageData)
        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.JPEG,
            filename="test.jpg",
            ownerId=MemberId(id="12345678-1234-5678-1234-567812345678"),
        )

        # Act & Assert - should not raise
        service.ValidateImageSize(image)

    def test_ValidateImageSize_WithOversizedImage_ShouldRaiseException(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.maxFileSizeBytes = 100  # Very small limit
        service = ImageValidationService(config)

        # Create a large image content
        imageData = b"x" * 1000  # 1000 bytes
        binary = io.BytesIO(imageData)
        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.JPEG,
            filename="large.jpg",
            ownerId=MemberId(id="22345678-1234-5678-1234-567812345678"),
        )

        # Act & Assert
        with pytest.raises(ImageContentTooLargeException) as excInfo:
            service.ValidateImageSize(image)

        assert excInfo.value.code == 413

    def test_ValidateIsImage_WithValidImage_ShouldPass(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        service = ImageValidationService(config)

        # Create a valid in-memory image
        img = Image.new("RGB", (100, 100), color="red")
        binary = io.BytesIO()
        img.save(binary, format="JPEG")
        binary.seek(0)

        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.JPEG,
            filename="valid.jpg",
            ownerId=MemberId(id="32345678-1234-5678-1234-567812345678"),
        )

        # Act & Assert - should not raise
        service.ValidateIsImage(image)

        # Verify stream was reset to beginning
        assert binary.tell() == 0

    def test_ValidateIsImage_WithInvalidImage_ShouldRaiseException(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        service = ImageValidationService(config)

        # Create invalid binary content (not an image)
        binary = io.BytesIO(b"not an image content")
        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.JPEG,
            filename="invalid.jpg",
            ownerId=MemberId(id="42345678-1234-5678-1234-567812345678"),
        )

        # Act & Assert
        with pytest.raises(ImageNotValidException) as excInfo:
            service.ValidateIsImage(image)

        assert excInfo.value.code == 422

    def test_ValidateImageContent_WithAllValidations_ShouldPass(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.allowedMimeTypes = [MimeType.JPEG, MimeType.PNG]
        config.maxFileSizeBytes = 10_000_000  # 10 MB
        service = ImageValidationService(config)

        # Create a valid in-memory image
        img = Image.new("RGB", (100, 100), color="blue")
        binary = io.BytesIO()
        img.save(binary, format="PNG")
        binary.seek(0)

        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.PNG,
            filename="valid.png",
            ownerId=MemberId(id="52345678-1234-5678-1234-567812345678"),
        )

        # Act & Assert - should not raise
        service.ValidateImageContent(image)

    def test_ValidateImageContent_WithInvalidMimeType_ShouldRaiseException(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.allowedMimeTypes = [MimeType.JPEG]
        config.maxFileSizeBytes = 10_000_000
        service = ImageValidationService(config)

        # Create a valid PNG image but with unsupported MIME type
        img = Image.new("RGB", (100, 100), color="green")
        binary = io.BytesIO()
        img.save(binary, format="PNG")
        binary.seek(0)

        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.PNG,  # Not in allowed types
            filename="test.png",
            ownerId=MemberId(id="62345678-1234-5678-1234-567812345678"),
        )

        # Act & Assert
        with pytest.raises(UnsupportedImageMimeTypeException):
            service.ValidateImageContent(image)


class TestImagePathService:
    """Tests for ImagePathService."""

    @patch("MiravejaCore.Shared.Storage.Domain.Services.datetime")
    @patch("MiravejaCore.Shared.Storage.Domain.Services.uuid.uuid4")
    def test_GenerateUniqueImagePath_ShouldFormatCorrectly(self, mockUuid, mockDatetime):
        # Arrange
        mockUuid.return_value = uuid.UUID("12345678-1234-5678-1234-567812345678")
        mockDate = MagicMock()
        mockDate.year = 2024
        mockDate.month = 3
        mockDatetime.now.return_value = mockDate

        ownerId = MemberId(id="72345678-1234-5678-1234-567812345678")
        binary = io.BytesIO(b"image data")
        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.JPEG,
            filename="test.jpg",
            ownerId=ownerId,
        )

        service = ImagePathService()

        # Act
        path = service.GenerateUniqueImagePath(ownerId, image)

        # Assert
        expectedPath = os.path.join(
            "members",
            "72345678-1234-5678-1234-567812345678",
            "images",
            "2024",
            "03",
            "12345678-1234-5678-1234-567812345678.jpg",
        )
        assert path == expectedPath

    @patch("MiravejaCore.Shared.Storage.Domain.Services.datetime")
    @patch("MiravejaCore.Shared.Storage.Domain.Services.uuid.uuid4")
    def test_GenerateUniqueImagePath_WithPngExtension_ShouldUsePngExtension(self, mockUuid, mockDatetime):
        # Arrange
        mockUuid.return_value = uuid.UUID("abcdefab-cdef-abcd-efab-cdefabcdefab")
        mockDate = MagicMock()
        mockDate.year = 2025
        mockDate.month = 12
        mockDatetime.now.return_value = mockDate

        ownerId = MemberId(id="82345678-1234-5678-1234-567812345678")
        binary = io.BytesIO(b"png image data")
        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.PNG,
            filename="photo.png",
            ownerId=ownerId,
        )

        service = ImagePathService()

        # Act
        path = service.GenerateUniqueImagePath(ownerId, image)

        # Assert
        assert path.endswith(".png")
        assert "82345678-1234-5678-1234-567812345678" in path
        assert "2025" in path
        assert "12" in path


class TestImageMetadataService:
    """Tests for ImageMetadataService."""

    @patch("MiravejaCore.Shared.Storage.Domain.Services.datetime")
    def test_PrepareImageMetadata_ShouldIncludeAllFields(self, mockDatetime):
        # Arrange
        mockNow = datetime(2024, 6, 15, 10, 30, 45, tzinfo=timezone.utc)
        mockDatetime.now.return_value = mockNow

        ownerId = MemberId(id="92345678-1234-5678-1234-567812345678")
        imageData = b"x" * 5000  # 5000 bytes
        binary = io.BytesIO(imageData)
        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.JPEG,
            filename="original-photo.jpg",
            ownerId=ownerId,
        )

        service = ImageMetadataService()

        # Act
        metadata = service.PrepareImageMetadata(image)

        # Assert
        assert metadata["ownerId"] == "92345678-1234-5678-1234-567812345678"
        assert metadata["originalFilename"] == "original-photo.jpg"
        assert metadata["mimeType"] == MimeType.JPEG
        assert metadata["sizeBytes"] == "5000"
        assert metadata["uploadedAt"] == "2024-06-15T10:30:45+00:00"

    @patch("MiravejaCore.Shared.Storage.Domain.Services.datetime")
    def test_PrepareImageMetadata_WithDifferentMimeType_ShouldReflectMimeType(self, mockDatetime):
        # Arrange
        mockNow = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        mockDatetime.now.return_value = mockNow

        ownerId = MemberId(id="a2345678-1234-5678-1234-567812345678")
        imageData = b"png content"
        binary = io.BytesIO(imageData)
        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.PNG,
            filename="image.png",
            ownerId=ownerId,
        )

        service = ImageMetadataService()

        # Act
        metadata = service.PrepareImageMetadata(image)

        # Assert
        assert metadata["mimeType"] == MimeType.PNG
        assert metadata["sizeBytes"] == str(len(imageData))


class TestSignedUrlService:
    """Tests for SignedUrlService."""

    def test_GetRelativeUrl_WithFullPresignedUrl_ShouldExtractPath(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.outsideEndpoint = "http://external.minio.example.com/"
        service = SignedUrlService(config)

        fullUrl = "http://minio:9000/bucket/members/owner-123/images/2024/03/test.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=..."

        # Act
        relativeUrl = service.GetRelativeUrl(fullUrl)

        # Assert
        expectedUrl = "http://external.minio.example.com/bucket/members/owner-123/images/2024/03/test.jpg"
        assert relativeUrl == expectedUrl

    def test_GetRelativeUrl_WithHttpsUrl_ShouldExtractPath(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.outsideEndpoint = "https://cdn.example.com/"
        service = SignedUrlService(config)

        fullUrl = "https://s3.amazonaws.com/my-bucket/path/to/image.png?AWSAccessKeyId=..."

        # Act
        relativeUrl = service.GetRelativeUrl(fullUrl)

        # Assert
        expectedUrl = "https://cdn.example.com/my-bucket/path/to/image.png"
        assert relativeUrl == expectedUrl

    def test_GetRelativeUrl_WithLeadingSlash_ShouldStripSlash(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.outsideEndpoint = "http://localhost:9001/"
        service = SignedUrlService(config)

        fullUrl = "http://localhost:9000//images/test.jpg"

        # Act
        relativeUrl = service.GetRelativeUrl(fullUrl)

        # Assert
        assert not relativeUrl.startswith("//")
        assert relativeUrl.startswith("http://localhost:9001/")
