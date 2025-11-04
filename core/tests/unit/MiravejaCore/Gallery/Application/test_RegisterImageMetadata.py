"""
Unit tests for RegisterImageMetadata command and handler.

This module contains tests for registering image metadata including
validation, repository interactions, and error handling scenarios.
"""

from typing import Type
from unittest.mock import Mock, AsyncMock
import pytest
from pydantic import ValidationError

from MiravejaCore.Gallery.Application.RegisterImageMetadata import (
    RegisterImageMetadataCommand,
    RegisterImageMetadataHandler,
)
from MiravejaCore.Gallery.Application.RegisterGenerationMetadata import (
    RegisterGenerationMetadataCommand,
    RegisterGenerationMetadataHandler,
)
from MiravejaCore.Gallery.Domain.Enums import ImageRepositoryType
from MiravejaCore.Gallery.Domain.Exceptions import ImageMetadataUriAlreadyExistsException
from MiravejaCore.Gallery.Domain.Interfaces import IImageMetadataRepository
from MiravejaCore.Gallery.Domain.Models import ImageMetadata
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId, VectorId


class TestRegisterImageMetadataCommand:
    """Tests for RegisterImageMetadataCommand validation."""

    def test_ValidCommand_ShouldCreateSuccessfully(self):
        """Test that a valid command creates successfully."""
        # Arrange & Act
        valid_uuid = "12345678-1234-1234-1234-123456789abc"
        command = RegisterImageMetadataCommand(
            ownerId=valid_uuid,
            title="Test Image",
            subtitle="Test Subtitle",
            description="Test Description",
            width=1920,
            height=1080,
            repositoryType=ImageRepositoryType.S3,
            uri="https://example.com/image.jpg",
            isAiGenerated=False,
            generationMetadata=None,
            vectorId=None,
        )

        # Assert
        assert command.ownerId == valid_uuid
        assert command.title == "Test Image"
        assert command.subtitle == "Test Subtitle"
        assert command.description == "Test Description"
        assert command.width == 1920
        assert command.height == 1080
        assert command.repositoryType == ImageRepositoryType.S3
        assert command.uri == "https://example.com/image.jpg"
        assert command.isAiGenerated is False
        assert command.generationMetadata is None
        assert command.vectorId is None

    def test_ValidCommandWithOptionalFields_ShouldCreateSuccessfully(self):
        """Test that a valid command with optional fields creates successfully."""
        # Arrange
        generation_metadata = Mock(spec=RegisterGenerationMetadataCommand)
        vector_id = VectorId(id=123)

        # Act
        command = RegisterImageMetadataCommand(
            ownerId="87654321-4321-4321-4321-cba987654321",
            title="AI Generated Image",
            subtitle="AI Subtitle",
            description="AI generated description",
            width=512,
            height=512,
            repositoryType=ImageRepositoryType.S3,
            uri="https://example.com/ai-image.jpg",
            isAiGenerated=True,
            generationMetadata=generation_metadata,
            vectorId=vector_id,
        )

        # Assert
        assert command.generationMetadata == generation_metadata
        assert command.vectorId == vector_id
        assert command.isAiGenerated is True

    def test_EmptyTitle_ShouldRaiseValidationError(self):
        """Test that empty title raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegisterImageMetadataCommand(
                ownerId="11111111-1111-1111-1111-111111111111",
                title="",  # Empty title
                subtitle="Test Subtitle",
                description="Test Description",
                width=1920,
                height=1080,
                repositoryType=ImageRepositoryType.S3,
                uri="https://example.com/image.jpg",
                isAiGenerated=False,
                generationMetadata=None,
                vectorId=None,
            )

        assert "String should have at least 1 character" in str(exc_info.value)

    def test_ZeroWidth_ShouldRaiseValidationError(self):
        """Test that zero width raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegisterImageMetadataCommand(
                ownerId="99999999-9999-9999-9999-999999999999",
                title="Test Image",
                subtitle="Test Subtitle",
                description="Test Description",
                width=0,  # Invalid width
                height=1080,
                repositoryType=ImageRepositoryType.S3,
                uri="https://example.com/image.jpg",
                isAiGenerated=False,
                generationMetadata=None,
                vectorId=None,
            )

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_NegativeHeight_ShouldRaiseValidationError(self):
        """Test that negative height raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegisterImageMetadataCommand(
                ownerId="99999999-9999-9999-9999-999999999999",
                title="Test Image",
                subtitle="Test Subtitle",
                description="Test Description",
                width=1920,
                height=-100,  # Invalid height
                repositoryType=ImageRepositoryType.S3,
                uri="https://example.com/image.jpg",
                isAiGenerated=False,
                generationMetadata=None,
                vectorId=None,
            )

        assert "Input should be greater than 0" in str(exc_info.value)

    def test_TitleTooLong_ShouldRaiseValidationError(self):
        """Test that title exceeding max length raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegisterImageMetadataCommand(
                ownerId="99999999-9999-9999-9999-999999999999",
                title="x" * 201,  # Exceeds max length of 200
                subtitle="Test Subtitle",
                description="Test Description",
                width=1920,
                height=1080,
                repositoryType=ImageRepositoryType.S3,
                uri="https://example.com/image.jpg",
                isAiGenerated=False,
                generationMetadata=None,
                vectorId=None,
            )

        assert "String should have at most 200 characters" in str(exc_info.value)


class TestRegisterImageMetadataHandler:
    """Tests for RegisterImageMetadataHandler business logic."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for the handler."""
        mock_uow_factory = Mock()
        mock_uow = Mock()
        mock_repository = Mock()
        mock_generation_handler = Mock(spec=RegisterGenerationMetadataHandler)
        mock_image_content_repository = AsyncMock()  # Async methods need AsyncMock
        mock_event_dispatcher = Mock(spec=EventDispatcher)
        mock_logger = Mock()

        # Setup UoW chain
        mock_uow_factory.Create.return_value.__enter__ = Mock(return_value=mock_uow)
        mock_uow_factory.Create.return_value.__exit__ = Mock(return_value=None)
        mock_uow.GetRepository.return_value = mock_repository

        return {
            "uow_factory": mock_uow_factory,
            "uow": mock_uow,
            "repository": mock_repository,
            "generation_handler": mock_generation_handler,
            "image_content_repository": mock_image_content_repository,
            "event_dispatcher": mock_event_dispatcher,
            "logger": mock_logger,
        }

    @pytest.fixture
    def handler(self, mock_dependencies):
        """Create handler instance with mocked dependencies."""
        return RegisterImageMetadataHandler(
            databaseManagerFactory=mock_dependencies["uow_factory"],
            # For testing purposes, we'll pass the interface type directly
            tImageMetadataRepository=IImageMetadataRepository,
            registerGenerationMetadataHandler=mock_dependencies["generation_handler"],
            imageContentRepository=mock_dependencies["image_content_repository"],
            eventDispatcher=mock_dependencies["event_dispatcher"],
            logger=mock_dependencies["logger"],
        )

    @pytest.mark.asyncio
    async def test_HandleValidCommand_ShouldRegisterImageMetadata(self, handler, mock_dependencies):
        """Test successful image metadata registration."""
        # Arrange
        command = RegisterImageMetadataCommand(
            ownerId="99999999-9999-9999-9999-999999999999",
            title="Test Image",
            subtitle="Test Subtitle",
            description="Test Description",
            width=1920,
            height=1080,
            repositoryType=ImageRepositoryType.S3,
            uri="https://example.com/image.jpg",
            isAiGenerated=False,
            generationMetadata=None,
            vectorId=None,
        )

        image_id = ImageMetadataId(id=42)
        mock_dependencies["repository"].FindByUri.return_value = None  # No existing image
        mock_dependencies["repository"].GenerateNewId.return_value = image_id

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result == 42
        mock_dependencies["repository"].FindByUri.assert_called_once_with(command.uri)
        mock_dependencies["repository"].GenerateNewId.assert_called_once()
        mock_dependencies["repository"].Save.assert_called_once()
        assert mock_dependencies["uow"].Commit.call_count == 2  # Called twice: after save and after generation
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()
        mock_dependencies["logger"].Info.assert_called()

    @pytest.mark.asyncio
    async def test_HandleDuplicateUri_ShouldRaiseImageMetadataUriAlreadyExistsException(
        self, handler, mock_dependencies
    ):
        """Test that duplicate URI raises appropriate exception."""
        # Arrange
        command = RegisterImageMetadataCommand(
            ownerId="99999999-9999-9999-9999-999999999999",
            title="Test Image",
            subtitle="Test Subtitle",
            description="Test Description",
            width=1920,
            height=1080,
            repositoryType=ImageRepositoryType.S3,
            uri="https://example.com/existing-image.jpg",
            isAiGenerated=False,
            generationMetadata=None,
            vectorId=None,
        )

        existing_image = Mock(spec=ImageMetadata)
        mock_dependencies["repository"].FindByUri.return_value = existing_image

        # Act & Assert
        with pytest.raises(ImageMetadataUriAlreadyExistsException) as exc_info:
            await handler.Handle(command)

        assert str(exc_info.value) == f"Image metadata with URI '{command.uri}' already exists."
        mock_dependencies["repository"].FindByUri.assert_called_once_with(command.uri)
        mock_dependencies["repository"].Save.assert_not_called()
        mock_dependencies["uow"].Commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_HandleAiGeneratedImageWithMetadata_ShouldCallGenerationHandler(self, handler, mock_dependencies):
        """Test that AI-generated images with metadata call the generation handler."""
        # Arrange
        generation_metadata = Mock(spec=RegisterGenerationMetadataCommand)
        command = RegisterImageMetadataCommand(
            ownerId="99999999-9999-9999-9999-999999999999",
            title="AI Generated Image",
            subtitle="AI Subtitle",
            description="AI generated description",
            width=512,
            height=512,
            repositoryType=ImageRepositoryType.S3,
            uri="https://example.com/ai-image.jpg",
            isAiGenerated=True,
            generationMetadata=generation_metadata,
            vectorId=None,
        )

        image_id = ImageMetadataId(id=123)
        mock_dependencies["repository"].FindByUri.return_value = None
        mock_dependencies["repository"].GenerateNewId.return_value = image_id

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result == 123
        mock_dependencies["generation_handler"].Handle.assert_called_once_with(
            imageId=image_id, command=generation_metadata
        )
        mock_dependencies["repository"].Save.assert_called_once()
        assert mock_dependencies["uow"].Commit.call_count == 2  # Called twice: after save and after generation
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleAiGeneratedImageWithoutMetadata_ShouldNotCallGenerationHandler(
        self, handler, mock_dependencies
    ):
        """Test that AI-generated images without metadata don't call generation handler."""
        # Arrange
        command = RegisterImageMetadataCommand(
            ownerId="99999999-9999-9999-9999-999999999999",
            title="AI Generated Image",
            subtitle="AI Subtitle",
            description="AI generated description",
            width=512,
            height=512,
            repositoryType=ImageRepositoryType.S3,
            uri="https://example.com/ai-image.jpg",
            isAiGenerated=True,
            generationMetadata=None,  # No generation metadata
            vectorId=None,
        )

        image_id = ImageMetadataId(id=456)
        mock_dependencies["repository"].FindByUri.return_value = None
        mock_dependencies["repository"].GenerateNewId.return_value = image_id

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result == 456
        mock_dependencies["generation_handler"].Handle.assert_not_called()
        mock_dependencies["repository"].Save.assert_called_once()
        assert (
            mock_dependencies["uow"].Commit.call_count == 2
        )  # Still called twice (second commit even when no generation)
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleNonAiGeneratedImage_ShouldNotCallGenerationHandler(self, handler, mock_dependencies):
        """Test that non-AI generated images don't call generation handler."""
        # Arrange
        command = RegisterImageMetadataCommand(
            ownerId="99999999-9999-9999-9999-999999999999",
            title="Regular Image",
            subtitle="Regular Subtitle",
            description="Regular description",
            width=1920,
            height=1080,
            repositoryType=ImageRepositoryType.S3,
            uri="https://example.com/regular-image.jpg",
            isAiGenerated=False,
            generationMetadata=None,
            vectorId=None,
        )

        image_id = ImageMetadataId(id=789)
        mock_dependencies["repository"].FindByUri.return_value = None
        mock_dependencies["repository"].GenerateNewId.return_value = image_id

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result == 789
        mock_dependencies["generation_handler"].Handle.assert_not_called()
        mock_dependencies["repository"].Save.assert_called_once()
        assert (
            mock_dependencies["uow"].Commit.call_count == 2
        )  # Still called twice (second commit even when no generation)
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()
