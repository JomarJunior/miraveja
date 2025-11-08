"""
Unit tests for Storage Domain Interfaces.

Tests IBucketService and IStorageService abstract interfaces.
"""

import io
from unittest.mock import MagicMock
import pytest

from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Shared.Storage.Domain.Enums import MimeType
from MiravejaCore.Shared.Storage.Domain.Interfaces import (
    IBucketService,
    IStorageService,
)
from MiravejaCore.Shared.Storage.Domain.Models import ImageContent


class TestIBucketService:
    """Tests for IBucketService interface."""

    def test_InitializeWithConfig_ShouldSetAttributes(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.bucketName = "test-bucket"
        config.region = "us-east-1"

        # Create a concrete implementation for testing
        class ConcreteBucketService(IBucketService):
            def EnsureBucketExists(self) -> None:
                pass

        # Act
        service = ConcreteBucketService(config)

        # Assert
        assert service.config == config
        assert service.bucketName == "test-bucket"
        assert service.region == "us-east-1"

    def test_EnsureBucketExists_ShouldBeAbstractMethod(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.bucketName = "bucket"
        config.region = "region"

        # Act & Assert - should not be able to instantiate directly
        with pytest.raises(TypeError) as excInfo:
            IBucketService(config)  # type: ignore

        assert "Can't instantiate abstract class" in str(excInfo.value)

    def test_ConcreteImplementation_MustImplementEnsureBucketExists(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.bucketName = "bucket"
        config.region = "region"

        # Create incomplete implementation
        class IncompleteBucketService(IBucketService):
            pass

        # Act & Assert
        with pytest.raises(TypeError) as excInfo:
            IncompleteBucketService(config)  # type: ignore

        assert "Can't instantiate abstract class" in str(excInfo.value)

    def test_ConcreteImplementation_CanCallEnsureBucketExists(self):
        # Arrange
        config = MagicMock(spec=MinIoConfig)
        config.bucketName = "my-bucket"
        config.region = "eu-west-1"

        class ConcreteBucketService(IBucketService):
            def __init__(self, config: MinIoConfig):
                super().__init__(config)
                self.ensureCalled = False

            def EnsureBucketExists(self) -> None:
                self.ensureCalled = True

        # Act
        service = ConcreteBucketService(config)
        service.EnsureBucketExists()

        # Assert
        assert service.ensureCalled is True


class TestIStorageService:
    """Tests for IStorageService interface."""

    def test_UploadImage_ShouldBeAbstractMethod(self):
        # Act & Assert - should not be able to instantiate directly
        with pytest.raises(TypeError) as excInfo:
            IStorageService()  # type: ignore

        assert "Can't instantiate abstract class" in str(excInfo.value)

    def test_DeleteImage_ShouldBeAbstractMethod(self):
        # Arrange
        class PartialStorageService(IStorageService):
            def UploadImage(self, imageContent: ImageContent) -> None:
                pass

            def GetPresignedUrl(self, imageUri: str, expiresInSeconds: int) -> str:
                return ""

        # Act & Assert - missing DeleteImage
        with pytest.raises(TypeError) as excInfo:
            PartialStorageService()  # type: ignore

        assert "Can't instantiate abstract class" in str(excInfo.value)

    def test_GetPresignedUrl_ShouldBeAbstractMethod(self):
        # Arrange
        class PartialStorageService(IStorageService):
            def UploadImage(self, imageContent: ImageContent) -> None:
                pass

            def DeleteImage(self, imageUri: str) -> None:
                pass

        # Act & Assert - missing GetPresignedUrl
        with pytest.raises(TypeError) as excInfo:
            PartialStorageService()  # type: ignore

        assert "Can't instantiate abstract class" in str(excInfo.value)

    def test_ConcreteImplementation_MustImplementAllMethods(self):
        # Arrange
        class ConcreteStorageService(IStorageService):
            def UploadImage(self, imageContent: ImageContent) -> None:
                pass

            def DeleteImage(self, imageUri: str) -> None:
                pass

            def GetPresignedUrl(self, imageUri: str, expiresInSeconds: int) -> str:
                return f"https://example.com/{imageUri}?expires={expiresInSeconds}"

        # Act
        service = ConcreteStorageService()

        # Assert - should be able to instantiate
        assert service is not None
        assert isinstance(service, IStorageService)

    def test_ConcreteImplementation_UploadImageCanAcceptImageContent(self):
        # Arrange
        class ConcreteStorageService(IStorageService):
            def __init__(self):
                self.uploadedImage = None

            def UploadImage(self, imageContent: ImageContent) -> None:
                self.uploadedImage = imageContent

            def DeleteImage(self, imageUri: str) -> None:
                pass

            def GetPresignedUrl(self, imageUri: str, expiresInSeconds: int) -> str:
                return ""

        service = ConcreteStorageService()

        binary = io.BytesIO(b"image data")
        image = ImageContent.model_construct(
            binary=binary,
            mimeType=MimeType.JPEG,
            filename="test.jpg",
            ownerId=MemberId(id="12345678-1234-5678-1234-567812345678"),
        )

        # Act
        service.UploadImage(image)

        # Assert
        assert service.uploadedImage == image

    def test_ConcreteImplementation_DeleteImageCanAcceptUri(self):
        # Arrange
        class ConcreteStorageService(IStorageService):
            def __init__(self):
                self.deletedUri = None

            def UploadImage(self, imageContent: ImageContent) -> None:
                pass

            def DeleteImage(self, imageUri: str) -> None:
                self.deletedUri = imageUri

            def GetPresignedUrl(self, imageUri: str, expiresInSeconds: int) -> str:
                return ""

        service = ConcreteStorageService()
        testUri = "s3://bucket/path/to/image.jpg"

        # Act
        service.DeleteImage(testUri)

        # Assert
        assert service.deletedUri == testUri

    def test_ConcreteImplementation_GetPresignedUrlReturnsString(self):
        # Arrange
        class ConcreteStorageService(IStorageService):
            def UploadImage(self, imageContent: ImageContent) -> None:
                pass

            def DeleteImage(self, imageUri: str) -> None:
                pass

            def GetPresignedUrl(self, imageUri: str, expiresInSeconds: int) -> str:
                return f"https://signed.url/{imageUri}?expires={expiresInSeconds}"

        service = ConcreteStorageService()

        # Act
        url = service.GetPresignedUrl("path/to/image.png", 3600)

        # Assert
        assert isinstance(url, str)
        assert "path/to/image.png" in url
        assert "3600" in url
