import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from botocore.exceptions import ClientError

from MiravejaCore.Gallery.Infrastructure.MinIo.Repository import MinIoImageContentRepository
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class TestMinIoImageContentRepository:
    """Test cases for MinIoImageContentRepository."""

    def CreateMockBoto3Client(self) -> MagicMock:
        """Create a mock boto3 client for testing."""
        return MagicMock()

    def CreateMockLogger(self) -> MagicMock:
        """Create a mock logger for testing."""
        return MagicMock(spec=ILogger)

    def CreateTestMinIoConfig(self) -> MinIoConfig:
        """Create a test MinIO configuration."""
        return MinIoConfig(
            bucketName="test-bucket",
            endpoint="http://localhost:9000",
            outsideEndpoint="http://minio.local:9000",
            accessKey="minioadmin",
            secretKey="minioadmin",
            maxFileSizeBytes=10485760,  # 10MB
            presignedUrlExpirationSeconds=3600,
        )

    def test_InitializeWithExistingBucket_ShouldLogInfo(self):
        """Test initialization when bucket already exists."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()

        # Act
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)

        # Assert
        mockBoto3Client.list_buckets.assert_called_once()
        mockBoto3Client.create_bucket.assert_not_called()
        mockLogger.Info.assert_called_with("Bucket test-bucket already exists")

    def test_InitializeWithNonExistingBucket_ShouldCreateBucket(self):
        """Test initialization when bucket doesn't exist."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": []}
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()

        # Act
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)

        # Assert
        mockBoto3Client.list_buckets.assert_called_once()
        mockBoto3Client.create_bucket.assert_called_once_with(Bucket="test-bucket", ObjectLockEnabledForBucket=True)
        mockLogger.Info.assert_any_call("Creating bucket test-bucket")

    def test_GetImageKey_ShouldExtractKeyFromUri(self):
        """Test that GetImageKey correctly extracts the key from an image URI."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)

        # Act
        imageUri = "http://minio.local:9000/test-bucket/images/user123/image456.png"
        key = repository._GetImageKey(imageUri)

        # Assert
        assert key == "images/user123/image456.png"

    @pytest.mark.asyncio
    async def test_GetPresignedGetUrl_ShouldGenerateValidUrl(self):
        """Test generating a presigned GET URL."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        mockBoto3Client.generate_presigned_url.return_value = "https://presigned-get-url.com"
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)

        # Act
        presignedUrl = await repository.GetPresignedGetUrl("images/test.png")

        # Assert
        assert presignedUrl == "https://presigned-get-url.com"
        mockBoto3Client.generate_presigned_url.assert_called_once_with(
            "get_object", Params={"Bucket": "test-bucket", "Key": "images/test.png"}, ExpiresIn=3600
        )
        mockLogger.Info.assert_any_call("Generating presigned GET URL for images/test.png")

    @pytest.mark.asyncio
    async def test_GetPresignedGetUrlWithException_ShouldLogErrorAndReraise(self):
        """Test that GetPresignedGetUrl handles exceptions correctly."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        testError = RuntimeError("Failed to generate URL")
        mockBoto3Client.generate_presigned_url.side_effect = testError
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await repository.GetPresignedGetUrl("images/test.png")

        assert exc_info.value == testError
        mockLogger.Error.assert_called_once_with(f"Error generating presigned GET URL: {testError}")

    @pytest.mark.asyncio
    async def test_GetPresignedPostUrl_ShouldGenerateValidPostData(self):
        """Test generating a presigned POST URL with fields and conditions."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        mockBoto3Client.generate_presigned_post.return_value = {
            "url": "https://presigned-post-url.com",
            "fields": {"key": "images/test.png", "AWSAccessKeyId": "access123"},
        }
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        testOwnerId = MemberId(id="12345678-1234-1234-1234-123456789012")

        # Act
        presignedPost = await repository.GetPresignedPostUrl("images/test.png", testOwnerId)

        # Assert
        assert presignedPost["url"] == "https://presigned-post-url.com"
        assert "fields" in presignedPost
        mockBoto3Client.generate_presigned_post.assert_called_once()
        call_args = mockBoto3Client.generate_presigned_post.call_args
        assert call_args[1]["Bucket"] == "test-bucket"
        assert call_args[1]["Key"] == "images/test.png"
        assert call_args[1]["Fields"]["x-amz-meta-owner-id"] == str(testOwnerId.id)
        assert call_args[1]["ExpiresIn"] == 3600
        mockLogger.Info.assert_any_call("Generating presigned POST URL for images/test.png")

    @pytest.mark.asyncio
    async def test_GetPresignedPostUrlWithException_ShouldLogErrorAndReraise(self):
        """Test that GetPresignedPostUrl handles exceptions correctly."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        testError = RuntimeError("Failed to generate POST URL")
        mockBoto3Client.generate_presigned_post.side_effect = testError
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        testOwnerId = MemberId(id="12345678-1234-1234-1234-123456789012")

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await repository.GetPresignedPostUrl("images/test.png", testOwnerId)

        assert exc_info.value == testError
        mockLogger.Error.assert_called_once_with(f"Error generating presigned POST URL: {testError}")

    @pytest.mark.asyncio
    async def test_GetMetadata_ShouldReturnMetadataDict(self):
        """Test fetching metadata for an image."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        mockBoto3Client.head_object.return_value = {"Metadata": {"owner-id": "user123", "content-type": "image/png"}}
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        imageUri = "http://minio.local:9000/test-bucket/images/test.png"

        # Act
        metadata = await repository.GetMetadata(imageUri)

        # Assert
        assert metadata == {"owner-id": "user123", "content-type": "image/png"}
        mockBoto3Client.head_object.assert_called_once_with(Bucket="test-bucket", Key="images/test.png")
        mockLogger.Info.assert_any_call("Fetching metadata for images/test.png")

    @pytest.mark.asyncio
    async def test_GetMetadataWithNoSuchKey_ShouldReturnEmptyDict(self):
        """Test that GetMetadata returns empty dict when object doesn't exist."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        # Create mock NoSuchKey exception
        mockBoto3Client.exceptions.NoSuchKey = type("NoSuchKey", (Exception,), {})
        mockBoto3Client.head_object.side_effect = mockBoto3Client.exceptions.NoSuchKey()
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        imageUri = "http://minio.local:9000/test-bucket/images/missing.png"

        # Act
        metadata = await repository.GetMetadata(imageUri)

        # Assert
        assert metadata == {}
        mockLogger.Warning.assert_called_once_with("Object images/missing.png not found in bucket test-bucket")

    @pytest.mark.asyncio
    async def test_GetMetadataWithException_ShouldLogErrorAndReraise(self):
        """Test that GetMetadata handles general exceptions correctly that are NOT NoSuchKey."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        # Setup NoSuchKey exception type
        mockBoto3Client.exceptions = MagicMock()
        mockBoto3Client.exceptions.NoSuchKey = type("NoSuchKey", (Exception,), {})

        testError = RuntimeError("S3 connection error")
        mockBoto3Client.head_object.side_effect = testError
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        imageUri = "http://minio.local:9000/test-bucket/images/test.png"

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await repository.GetMetadata(imageUri)

        assert exc_info.value == testError
        mockLogger.Error.assert_called_once_with(f"Error fetching metadata for images/test.png: {testError}")

    @pytest.mark.asyncio
    async def test_Delete_ShouldCallDeleteObject(self):
        """Test deleting an image."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        imageUri = "http://minio.local:9000/test-bucket/images/test.png"

        # Act
        await repository.Delete(imageUri)

        # Assert
        mockBoto3Client.delete_object.assert_called_once_with(Bucket="test-bucket", Key="images/test.png")
        mockLogger.Info.assert_any_call("Deleting object images/test.png from bucket test-bucket")
        mockLogger.Info.assert_any_call("Successfully deleted images/test.png")

    @pytest.mark.asyncio
    async def test_DeleteWithException_ShouldLogErrorAndReraise(self):
        """Test that Delete handles exceptions correctly."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        testError = RuntimeError("Delete failed")
        mockBoto3Client.delete_object.side_effect = testError
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        imageUri = "http://minio.local:9000/test-bucket/images/test.png"

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await repository.Delete(imageUri)

        assert exc_info.value == testError
        mockLogger.Error.assert_called_once_with(f"Error deleting object images/test.png: {testError}")

    @pytest.mark.asyncio
    async def test_ExistsWhenObjectExists_ShouldReturnTrue(self):
        """Test that Exists returns True when object exists."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        mockBoto3Client.head_object.return_value = {}
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        imageUri = "http://minio.local:9000/test-bucket/images/test.png"

        # Act
        exists = await repository.Exists(imageUri)

        # Assert
        assert exists is True
        mockBoto3Client.head_object.assert_called_once_with(Bucket="test-bucket", Key="images/test.png")
        mockLogger.Info.assert_any_call("Object images/test.png exists")

    @pytest.mark.asyncio
    async def test_ExistsWhenObjectNotFound_ShouldReturnFalse(self):
        """Test that Exists returns False when object is not found."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        mockBoto3Client.head_object.side_effect = Exception("404 Not Found")
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        imageUri = "http://minio.local:9000/test-bucket/images/missing.png"

        # Act
        exists = await repository.Exists(imageUri)

        # Assert
        assert exists is False
        mockLogger.Error.assert_called_once()
        mockLogger.Info.assert_any_call("Object images/missing.png does not exist")

    @pytest.mark.asyncio
    async def test_ExistsWithOtherException_ShouldReraise(self):
        """Test that Exists reraises non-NotFound exceptions."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        testError = RuntimeError("Connection error")
        mockBoto3Client.head_object.side_effect = testError
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        imageUri = "http://minio.local:9000/test-bucket/images/test.png"

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await repository.Exists(imageUri)

        assert exc_info.value == testError

    @pytest.mark.asyncio
    async def test_IsOwnedByWhenOwned_ShouldReturnTrue(self):
        """Test that IsOwnedBy returns True when object is owned by the member."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        testOwnerId = MemberId(id="12345678-1234-1234-1234-123456789012")
        mockBoto3Client.head_object.return_value = {"Metadata": {"owner-id": str(testOwnerId.id)}}
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        imageUri = "http://minio.local:9000/test-bucket/images/test.png"

        # Act
        isOwned = await repository.IsOwnedBy(imageUri, testOwnerId)

        # Assert
        assert isOwned is True
        mockLogger.Info.assert_any_call(f"Object {imageUri} is owned by member ID {testOwnerId.id}")

    @pytest.mark.asyncio
    async def test_IsOwnedByWhenNotOwned_ShouldReturnFalse(self):
        """Test that IsOwnedBy returns False when object is owned by a different member."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        testOwnerId = MemberId(id="12345678-1234-1234-1234-123456789012")
        differentOwnerId = MemberId(id="87654321-4321-4321-4321-210987654321")
        mockBoto3Client.head_object.return_value = {"Metadata": {"owner-id": str(differentOwnerId.id)}}
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        imageUri = "http://minio.local:9000/test-bucket/images/test.png"

        # Act
        isOwned = await repository.IsOwnedBy(imageUri, testOwnerId)

        # Assert
        assert isOwned is False
        mockLogger.Warning.assert_called_once_with(f"Object {imageUri} is not owned by member ID {testOwnerId.id}")

    @pytest.mark.asyncio
    async def test_IsOwnedByWithException_ShouldLogErrorAndReraise(self):
        """Test that IsOwnedBy handles exceptions correctly."""
        # Arrange
        mockBoto3Client = self.CreateMockBoto3Client()
        mockBoto3Client.list_buckets.return_value = {"Buckets": [{"Name": "test-bucket"}]}
        # Setup NoSuchKey exception type
        mockBoto3Client.exceptions = MagicMock()
        mockBoto3Client.exceptions.NoSuchKey = type("NoSuchKey", (Exception,), {})

        testError = RuntimeError("Metadata fetch failed")
        mockBoto3Client.head_object.side_effect = testError
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestMinIoConfig()
        repository = MinIoImageContentRepository(mockBoto3Client, testConfig, mockLogger)
        testOwnerId = MemberId(id="12345678-1234-1234-1234-123456789012")
        imageUri = "http://minio.local:9000/test-bucket/images/test.png"

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await repository.IsOwnedBy(imageUri, testOwnerId)

        assert exc_info.value == testError
        # IsOwnedBy calls GetMetadata which logs its own error, then IsOwnedBy logs another
        assert mockLogger.Error.call_count == 2
        mockLogger.Error.assert_any_call(f"Error fetching metadata for images/test.png: {testError}")
        mockLogger.Error.assert_any_call(f"Error checking ownership of object {imageUri}: {testError}")
