import pytest
from unittest.mock import MagicMock, AsyncMock
from MiravejaCore.Gallery.Application.GetPresignedPostUrl import (
    GetPresignedPostUrlCommand,
    GetPresignedPostUrlHandler,
)
from MiravejaCore.Gallery.Domain.Interfaces import IImageContentRepository
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Storage.Domain.Enums import MimeType
from MiravejaCore.Shared.Storage.Domain.Services import SignedUrlService


class TestGetPresignedPostUrlHandler:
    """Test cases for GetPresignedPostUrlHandler."""

    def CreateMockImageContentRepository(self) -> MagicMock:
        """Create a mock image content repository."""
        mock = MagicMock(spec=IImageContentRepository)
        mock.GetPresignedPostUrl = AsyncMock()
        return mock

    def CreateMockSignedUrlService(self) -> MagicMock:
        """Create a mock signed URL service."""
        return MagicMock(spec=SignedUrlService)

    def CreateMockLogger(self) -> MagicMock:
        """Create a mock logger."""
        return MagicMock(spec=ILogger)

    def CreateTestKeycloakUser(self) -> KeycloakUser:
        """Create a test Keycloak user."""
        return KeycloakUser(
            id="12345678-1234-1234-1234-123456789012",
            username="testuser",
            email="test@example.com",
            firstName="Test",
            lastName="User",
            emailVerified=True,
        )

    @pytest.mark.asyncio
    async def test_HandleWithValidCommand_ShouldReturnPresignedPostUrl(self):
        """Test handling a valid command returns presigned POST URL with relative URL."""
        # Arrange
        mockRepo = self.CreateMockImageContentRepository()
        mockRepo.GetPresignedPostUrl.return_value = {
            "url": "http://minio:9000/bucket/key",
            "fields": {
                "key": "12345678-1234-1234-1234-123456789012/gallery/test.png",
                "AWSAccessKeyId": "access123",
                "policy": "base64policy",
                "signature": "signature123",
            },
        }
        mockSignedUrlService = self.CreateMockSignedUrlService()
        mockSignedUrlService.GetRelativeUrl.return_value = "/api/storage/bucket/key"
        mockLogger = self.CreateMockLogger()
        handler = GetPresignedPostUrlHandler(mockRepo, mockSignedUrlService, mockLogger)
        testUser = self.CreateTestKeycloakUser()
        command = GetPresignedPostUrlCommand(filename="test.png", mimeType=MimeType.PNG, size=1024)

        # Act
        result = await handler.Handle(command, testUser)

        # Assert
        assert result["url"] == "/api/storage/bucket/key"
        assert result["fields"]["key"] == "12345678-1234-1234-1234-123456789012/gallery/test.png"
        mockRepo.GetPresignedPostUrl.assert_called_once()
        call_args = mockRepo.GetPresignedPostUrl.call_args
        assert call_args[1]["key"] == "12345678-1234-1234-1234-123456789012/gallery/test.png"
        assert call_args[1]["ownerId"].id == "12345678-1234-1234-1234-123456789012"
        mockSignedUrlService.GetRelativeUrl.assert_called_once_with("http://minio:9000/bucket/key")

    @pytest.mark.asyncio
    async def test_HandleWithDifferentFilename_ShouldGenerateCorrectKey(self):
        """Test that different filenames generate correct keys."""
        # Arrange
        mockRepo = self.CreateMockImageContentRepository()
        mockRepo.GetPresignedPostUrl.return_value = {
            "url": "http://minio:9000/bucket/key",
            "fields": {"key": "user-id/gallery/image.jpg"},
        }
        mockSignedUrlService = self.CreateMockSignedUrlService()
        mockSignedUrlService.GetRelativeUrl.return_value = "/api/storage/bucket/key"
        mockLogger = self.CreateMockLogger()
        handler = GetPresignedPostUrlHandler(mockRepo, mockSignedUrlService, mockLogger)
        testUser = self.CreateTestKeycloakUser()
        command = GetPresignedPostUrlCommand(filename="my-photo.jpg", mimeType=MimeType.JPEG, size=2048)

        # Act
        await handler.Handle(command, testUser)

        # Assert
        call_args = mockRepo.GetPresignedPostUrl.call_args
        expected_key = f"{testUser.id}/gallery/my-photo.jpg"
        assert call_args[1]["key"] == expected_key

    @pytest.mark.asyncio
    async def test_HandleWithException_ShouldLogErrorAndReraise(self):
        """Test that exceptions are logged and re-raised."""
        # Arrange
        mockRepo = self.CreateMockImageContentRepository()
        testError = RuntimeError("Failed to generate presigned URL")
        mockRepo.GetPresignedPostUrl.side_effect = testError
        mockSignedUrlService = self.CreateMockSignedUrlService()
        mockLogger = self.CreateMockLogger()
        handler = GetPresignedPostUrlHandler(mockRepo, mockSignedUrlService, mockLogger)
        testUser = self.CreateTestKeycloakUser()
        command = GetPresignedPostUrlCommand(filename="test.png", mimeType=MimeType.PNG, size=1024)

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await handler.Handle(command, testUser)

        assert exc_info.value == testError
        mockLogger.Error.assert_called_once()
        assert "Unexpected error during getting presigned post URL" in mockLogger.Error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_HandleWithDifferentMimeType_ShouldSucceed(self):
        """Test handling with different MIME types."""
        # Arrange
        mockRepo = self.CreateMockImageContentRepository()
        mockRepo.GetPresignedPostUrl.return_value = {
            "url": "http://minio:9000/bucket/key",
            "fields": {"key": "user/gallery/file.webp"},
        }
        mockSignedUrlService = self.CreateMockSignedUrlService()
        mockSignedUrlService.GetRelativeUrl.return_value = "/api/storage/bucket/key"
        mockLogger = self.CreateMockLogger()
        handler = GetPresignedPostUrlHandler(mockRepo, mockSignedUrlService, mockLogger)
        testUser = self.CreateTestKeycloakUser()
        command = GetPresignedPostUrlCommand(filename="file.webp", mimeType=MimeType.WEBP, size=4096)

        # Act
        result = await handler.Handle(command, testUser)

        # Assert
        assert result is not None
        assert "url" in result
        mockRepo.GetPresignedPostUrl.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleWithLargeFileSize_ShouldSucceed(self):
        """Test handling with large file size."""
        # Arrange
        mockRepo = self.CreateMockImageContentRepository()
        mockRepo.GetPresignedPostUrl.return_value = {
            "url": "http://minio:9000/bucket/key",
            "fields": {"key": "user/gallery/largefile.png"},
        }
        mockSignedUrlService = self.CreateMockSignedUrlService()
        mockSignedUrlService.GetRelativeUrl.return_value = "/api/storage/bucket/key"
        mockLogger = self.CreateMockLogger()
        handler = GetPresignedPostUrlHandler(mockRepo, mockSignedUrlService, mockLogger)
        testUser = self.CreateTestKeycloakUser()
        command = GetPresignedPostUrlCommand(filename="largefile.png", mimeType=MimeType.PNG, size=10485760)

        # Act
        result = await handler.Handle(command, testUser)

        # Assert
        assert result is not None
        mockRepo.GetPresignedPostUrl.assert_called_once()
