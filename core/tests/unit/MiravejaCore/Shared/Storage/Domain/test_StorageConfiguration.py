import io
import os
import pytest
from unittest.mock import patch, MagicMock

from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Shared.Storage.Domain.Enums import MimeType, Region
from MiravejaCore.Shared.Storage.Domain.Models import ImageContent, SIZE_1_MB


class TestMinIoConfig:
    """Test cases for MinIoConfig model."""

    def test_MaxFileSizeMBProperty_ShouldReturnSizeInMegabytes(self):
        """Test that maxFileSizeMB property returns correct value in MB."""
        # Arrange
        config = MinIoConfig(maxFileSizeBytes=5 * SIZE_1_MB)

        # Act
        result = config.maxFileSizeMB

        # Assert
        assert result == 5.0

    def test_EndpointUrlProperty_ShouldReturnFormattedUrl(self):
        """Test that endpointUrl property returns scheme and netloc."""
        # Arrange
        config = MinIoConfig(endpoint="http://localhost:9000/path/to/resource")

        # Act
        result = config.endpointUrl

        # Assert
        assert result == "http://localhost:9000"

    def test_EndpointUrlPropertyWithHttps_ShouldReturnHttpsUrl(self):
        """Test that endpointUrl property works with HTTPS."""
        # Arrange
        config = MinIoConfig(endpoint="https://storage.example.com:9000")

        # Act
        result = config.endpointUrl

        # Assert
        assert result == "https://storage.example.com:9000"

    @patch.dict(
        os.environ,
        {
            "MINIO_ENDPOINT": "http://test:9000",
            "MINIO_OUTSIDE_ENDPOINT": "https://test.example.com/storage/",
            "MINIO_ACCESS_KEY": "testkey",
            "MINIO_SECRET_KEY": "testsecret",
            "MINIO_BUCKET_NAME": "test-bucket",
            "MINIO_REGION": "us-east-1",
            "MINIO_MAX_FILE_SIZE": "52428800",
        },
        clear=True,
    )
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
        """Test that FromEnv creates config from all environment variables."""
        # Act
        config = MinIoConfig.FromEnv()

        # Assert
        assert config.endpoint == "http://test:9000"
        assert config.outsideEndpoint == "https://test.example.com/storage/"
        assert config.accessKey == "testkey"
        assert config.secretKey == "testsecret"
        assert config.bucketName == "test-bucket"
        assert config.region == Region.US_EAST_1
        assert config.maxFileSizeBytes == 52428800

    @patch.dict(os.environ, {}, clear=True)
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(self):
        """Test that FromEnv uses default values when no environment variables are set."""
        # Act
        config = MinIoConfig.FromEnv()

        # Assert
        assert config.endpoint == "http://localhost:9000"
        assert config.outsideEndpoint == "https://miraveja.127.0.0.1.nip.io/storage/"
        assert config.accessKey == "minioadmin"
        assert config.secretKey == "minioadmin"
        assert config.bucketName == "miraveja-bucket"
        assert config.region is None

    @patch.dict(os.environ, {"MINIO_ENDPOINT": "http://custom:9000"}, clear=True)
    def test_FromEnvWithNoRegion_ShouldSetRegionToNone(self):
        """Test that FromEnv sets region to None when MINIO_REGION is not set."""
        # Act
        config = MinIoConfig.FromEnv()

        # Assert
        assert config.region is None


class TestImageContent:
    """Test cases for ImageContent model."""

    def test_SizeMegabytesProperty_ShouldCalculateCorrectly(self):
        """Test that sizeMegabytes property calculates the correct size."""
        # Arrange
        # Create 2 MB of test data
        twoMbData = b"x" * (2 * 1024 * 1024)
        binary = io.BytesIO(twoMbData)
        memberId = MemberId.Generate()

        content = ImageContent.model_construct(
            binary=binary, mimeType=MimeType.JPEG, filename="test.jpg", ownerId=memberId
        )

        # Act
        sizeMb = content.sizeMegabytes

        # Assert
        assert sizeMb == 2.0

    def test_ExtensionPropertyWithUnknownMimeType_ShouldReturnFilenameExtension(self):
        """Test that extension property falls back to filename extension when MIME type is unknown."""
        # Arrange
        binary = io.BytesIO(b"test image data")
        memberId = MemberId.Generate()

        # Create ImageContent with custom MIME type that won't be recognized
        with patch("mimetypes.guess_extension", return_value=None):
            content = ImageContent.model_construct(
                binary=binary,
                mimeType=MimeType.JPEG,  # Use valid enum but mock will return None
                filename="test_image.xyz",  # Custom extension
                ownerId=memberId,
            )

            # Act
            result = content.extension

            # Assert
            assert result == ".xyz"

    def test_ExtensionPropertyWithNoExtensionInFilename_ShouldReturnEmptyString(self):
        """Test that extension property returns empty string when no extension found."""
        # Arrange
        binary = io.BytesIO(b"test image data")
        memberId = MemberId.Generate()

        # Mock both mimetypes.guess_extension and os.path.splitext
        with patch("mimetypes.guess_extension", return_value=None):
            content = ImageContent.model_construct(
                binary=binary, mimeType=MimeType.JPEG, filename="no_extension_file", ownerId=memberId  # No extension
            )

            # Act
            result = content.extension

            # Assert
            assert result == ""
