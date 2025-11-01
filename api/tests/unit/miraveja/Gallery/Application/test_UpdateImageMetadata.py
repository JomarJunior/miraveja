"""
Unit tests for UpdateImageMetadata command and handler.

This module contains tests for updating image metadata including
validation, repository interactions, and error handling scenarios.
"""

from typing import Type
from unittest.mock import Mock
import pytest
from pydantic import ValidationError

from Miraveja.Gallery.Application.UpdateImageMetadata import (
    UpdateImageMetadataCommand,
    UpdateImageMetadataHandler,
)
from Miraveja.Gallery.Domain.Exceptions import ImageMetadataNotFoundException
from Miraveja.Gallery.Domain.Interfaces import IImageMetadataRepository
from Miraveja.Gallery.Domain.Models import ImageMetadata
from Miraveja.Shared.Events.Application.EventDispatcher import EventDispatcher
from Miraveja.Shared.Identifiers.Models import ImageMetadataId, VectorId


class TestUpdateImageMetadataCommand:
    """Tests for UpdateImageMetadataCommand validation."""

    def test_ValidCommandWithAllFields_ShouldCreateSuccessfully(self):
        """Test that a valid command with all fields creates successfully."""
        # Arrange & Act
        command = UpdateImageMetadataCommand(
            title="Updated Title",
            subtitle="Updated Subtitle",
            description="Updated Description",
            vectorId=123,
            removeVectorId=False,
        )

        # Assert
        assert command.title == "Updated Title"
        assert command.subtitle == "Updated Subtitle"
        assert command.description == "Updated Description"
        assert command.vectorId == 123
        assert command.removeVectorId is False

    def test_ValidCommandWithNoFields_ShouldCreateSuccessfully(self):
        """Test that a valid command with no fields creates successfully."""
        # Arrange & Act
        command = UpdateImageMetadataCommand(
            title=None,
            subtitle=None,
            description=None,
            vectorId=None,
            removeVectorId=False,
        )

        # Assert
        assert command.title is None
        assert command.subtitle is None
        assert command.description is None
        assert command.vectorId is None
        assert command.removeVectorId is False

    def test_ValidCommandWithOnlyTitle_ShouldCreateSuccessfully(self):
        """Test that a valid command with only title creates successfully."""
        # Arrange & Act
        command = UpdateImageMetadataCommand(
            title="Only Title",
            subtitle=None,
            description=None,
            vectorId=None,
            removeVectorId=False,
        )

        # Assert
        assert command.title == "Only Title"
        assert command.subtitle is None
        assert command.description is None
        assert command.vectorId is None
        assert command.removeVectorId is False

    def test_ValidCommandWithRemoveVectorIdTrue_ShouldCreateSuccessfully(self):
        """Test that a valid command with removeVectorId=True creates successfully."""
        # Arrange & Act
        command = UpdateImageMetadataCommand(
            title=None,
            subtitle=None,
            description=None,
            vectorId=None,
            removeVectorId=True,
        )

        # Assert
        assert command.title is None
        assert command.subtitle is None
        assert command.description is None
        assert command.vectorId is None
        assert command.removeVectorId is True

    def test_EmptyTitle_ShouldRaiseValidationError(self):
        """Test that empty title raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UpdateImageMetadataCommand(
                title="", subtitle=None, description=None, vectorId=None, removeVectorId=False
            )  # Empty title

        assert "String should have at least 1 character" in str(exc_info.value)

    def test_TitleTooLong_ShouldRaiseValidationError(self):
        """Test that title exceeding max length raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UpdateImageMetadataCommand(
                title="x" * 201, subtitle=None, description=None, vectorId=None, removeVectorId=False
            )  # Exceeds max length of 200

        assert "String should have at most 200 characters" in str(exc_info.value)

    def test_EmptySubtitle_ShouldRaiseValidationError(self):
        """Test that empty subtitle raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UpdateImageMetadataCommand(
                title=None, subtitle="", description=None, vectorId=None, removeVectorId=False
            )  # Empty subtitle

        assert "String should have at least 1 character" in str(exc_info.value)

    def test_SubtitleTooLong_ShouldRaiseValidationError(self):
        """Test that subtitle exceeding max length raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UpdateImageMetadataCommand(
                title=None, subtitle="x" * 201, description=None, vectorId=None, removeVectorId=False
            )  # Exceeds max length of 200

        assert "String should have at most 200 characters" in str(exc_info.value)

    def test_DescriptionTooLong_ShouldRaiseValidationError(self):
        """Test that description exceeding max length raises ValidationError."""
        # Arrange, Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            UpdateImageMetadataCommand(
                title=None, subtitle=None, description="x" * 2001, vectorId=None, removeVectorId=False
            )  # Exceeds max length of 2000

        assert "String should have at most 2000 characters" in str(exc_info.value)

    def test_NegativeVectorId_ShouldCreateSuccessfully(self):
        """Test that negative vectorId is allowed (validation handled elsewhere)."""
        # Arrange & Act
        command = UpdateImageMetadataCommand(
            title=None, subtitle=None, description=None, vectorId=-1, removeVectorId=False
        )

        # Assert
        assert command.vectorId == -1


class TestUpdateImageMetadataHandler:
    """Tests for UpdateImageMetadataHandler business logic."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for the handler."""
        mock_uow_factory = Mock()
        mock_uow = Mock()
        mock_repository = Mock()
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
            "event_dispatcher": mock_event_dispatcher,
            "logger": mock_logger,
        }

    @pytest.fixture
    def handler(self, mock_dependencies):
        """Create handler instance with mocked dependencies."""
        return UpdateImageMetadataHandler(
            databaseManagerFactory=mock_dependencies["uow_factory"],
            tImageMetadataRepository=IImageMetadataRepository,
            eventDispatcher=mock_dependencies["event_dispatcher"],
            logger=mock_dependencies["logger"],
        )

    @pytest.fixture
    def mock_image_metadata(self):
        """Create a mock image metadata object."""
        mock_metadata = Mock(spec=ImageMetadata)
        mock_metadata.title = "Original Title"
        mock_metadata.subtitle = "Original Subtitle"
        mock_metadata.description = "Original Description"
        mock_metadata.vectorId = VectorId(id=456)
        return mock_metadata

    @pytest.mark.asyncio
    async def test_HandleUpdateTitle_ShouldUpdateTitleSuccessfully(
        self, handler, mock_dependencies, mock_image_metadata
    ):
        """Test successful title update."""
        # Arrange
        image_id = ImageMetadataId(id=123)
        command = UpdateImageMetadataCommand(
            title="New Title", subtitle=None, description=None, vectorId=None, removeVectorId=False
        )
        mock_dependencies["repository"].FindById.return_value = mock_image_metadata

        # Act
        await handler.Handle(image_id, command)

        # Assert
        mock_dependencies["repository"].FindById.assert_called_once_with(image_id)
        mock_image_metadata.Update.assert_called_once()
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()
        mock_dependencies["repository"].Save.assert_called_once_with(mock_image_metadata)
        mock_dependencies["uow"].Commit.assert_called_once()
        mock_dependencies["logger"].Info.assert_called()

    @pytest.mark.asyncio
    async def test_HandleUpdateSubtitle_ShouldUpdateSubtitleSuccessfully(
        self, handler, mock_dependencies, mock_image_metadata
    ):
        """Test successful subtitle update."""
        # Arrange
        image_id = ImageMetadataId(id=123)
        command = UpdateImageMetadataCommand(
            title=None, subtitle="New Subtitle", description=None, vectorId=None, removeVectorId=False
        )
        mock_dependencies["repository"].FindById.return_value = mock_image_metadata

        # Act
        await handler.Handle(image_id, command)

        # Assert
        mock_dependencies["repository"].FindById.assert_called_once_with(image_id)
        mock_image_metadata.Update.assert_called_once_with(
            title="Original Title", subtitle="New Subtitle", description="Original Description"
        )
        mock_dependencies["repository"].Save.assert_called_once_with(mock_image_metadata)
        mock_dependencies["uow"].Commit.assert_called_once()
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleUpdateDescription_ShouldUpdateDescriptionSuccessfully(
        self, handler, mock_dependencies, mock_image_metadata
    ):
        """Test successful description update."""
        # Arrange
        image_id = ImageMetadataId(id=123)
        command = UpdateImageMetadataCommand(
            title=None, subtitle=None, description="New Description", vectorId=None, removeVectorId=False
        )
        mock_dependencies["repository"].FindById.return_value = mock_image_metadata

        # Act
        await handler.Handle(image_id, command)

        # Assert
        mock_dependencies["repository"].FindById.assert_called_once_with(image_id)
        mock_image_metadata.Update.assert_called_once_with(
            title="Original Title", subtitle="Original Subtitle", description="New Description"
        )
        mock_dependencies["repository"].Save.assert_called_once_with(mock_image_metadata)
        mock_dependencies["uow"].Commit.assert_called_once()
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleUpdateAllFields_ShouldUpdateAllFieldsSuccessfully(
        self, handler, mock_dependencies, mock_image_metadata
    ):
        """Test successful update of all fields."""
        # Arrange
        image_id = ImageMetadataId(id=123)
        command = UpdateImageMetadataCommand(
            title="New Title",
            subtitle="New Subtitle",
            description="New Description",
            vectorId=None,
            removeVectorId=False,
        )
        mock_dependencies["repository"].FindById.return_value = mock_image_metadata

        # Act
        await handler.Handle(image_id, command)

        # Assert
        mock_image_metadata.Update.assert_called_once_with(
            title="New Title", subtitle="New Subtitle", description="New Description"
        )
        mock_dependencies["repository"].Save.assert_called_once_with(mock_image_metadata)
        mock_dependencies["uow"].Commit.assert_called_once()
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleImageMetadataNotFound_ShouldRaiseImageMetadataNotFoundException(
        self, handler, mock_dependencies
    ):
        """Test that missing image metadata raises appropriate exception."""
        # Arrange
        image_id = ImageMetadataId(id=999)
        command = UpdateImageMetadataCommand(
            title="New Title", subtitle=None, description=None, vectorId=None, removeVectorId=False
        )
        mock_dependencies["repository"].FindById.return_value = None  # Not found

        # Act & Assert
        with pytest.raises(ImageMetadataNotFoundException) as exc_info:
            await handler.Handle(image_id, command)

        assert str(exc_info.value) == f"Image metadata with ID 'id={image_id.id}' was not found."
        mock_dependencies["repository"].FindById.assert_called_once_with(image_id)
        mock_dependencies["repository"].Save.assert_not_called()
        mock_dependencies["uow"].Commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_HandleAssignVectorId_ShouldAssignVectorIdSuccessfully(
        self, handler, mock_dependencies, mock_image_metadata
    ):
        """Test successful vector ID assignment."""
        # Arrange
        image_id = ImageMetadataId(id=123)
        command = UpdateImageMetadataCommand(
            title=None, subtitle=None, description=None, vectorId=789, removeVectorId=False
        )
        mock_dependencies["repository"].FindById.return_value = mock_image_metadata

        # Act
        await handler.Handle(image_id, command)

        # Assert
        mock_image_metadata.AssignVectorId.assert_called_once()
        # Verify the VectorId was created correctly
        call_args = mock_image_metadata.AssignVectorId.call_args[0][0]
        assert call_args.id == 789
        mock_dependencies["repository"].Save.assert_called_once_with(mock_image_metadata)
        mock_dependencies["uow"].Commit.assert_called_once()
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleRemoveVectorIdWhenPresent_ShouldRemoveVectorIdSuccessfully(
        self, handler, mock_dependencies, mock_image_metadata
    ):
        """Test successful vector ID removal when present."""
        # Arrange
        image_id = ImageMetadataId(id=123)
        command = UpdateImageMetadataCommand(
            title=None, subtitle=None, description=None, vectorId=None, removeVectorId=True
        )
        mock_image_metadata.vectorId = VectorId(id=456)  # Has vector ID
        mock_dependencies["repository"].FindById.return_value = mock_image_metadata

        # Act
        await handler.Handle(image_id, command)

        # Assert
        mock_image_metadata.UnassignVectorId.assert_called_once()
        mock_dependencies["repository"].Save.assert_called_once_with(mock_image_metadata)
        mock_dependencies["uow"].Commit.assert_called_once()
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleRemoveVectorIdWhenNotPresent_ShouldNotCallUnassign(
        self, handler, mock_dependencies, mock_image_metadata
    ):
        """Test vector ID removal when not present doesn't call unassign."""
        # Arrange
        image_id = ImageMetadataId(id=123)
        command = UpdateImageMetadataCommand(
            title=None, subtitle=None, description=None, vectorId=None, removeVectorId=True
        )
        mock_image_metadata.vectorId = None  # No vector ID
        mock_dependencies["repository"].FindById.return_value = mock_image_metadata

        # Act
        await handler.Handle(image_id, command)

        # Assert
        mock_image_metadata.UnassignVectorId.assert_not_called()
        mock_dependencies["repository"].Save.assert_called_once_with(mock_image_metadata)
        mock_dependencies["uow"].Commit.assert_called_once()
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleNoUpdates_ShouldStillSaveAndCommit(self, handler, mock_dependencies, mock_image_metadata):
        """Test that handler still saves and commits even with no updates."""
        # Arrange
        image_id = ImageMetadataId(id=123)
        command = UpdateImageMetadataCommand(
            title=None, subtitle=None, description=None, vectorId=None, removeVectorId=False
        )  # No updates
        mock_dependencies["repository"].FindById.return_value = mock_image_metadata

        # Act
        await handler.Handle(image_id, command)

        # Assert
        # When no text fields are updated, the handler optimizes by not calling Update
        mock_image_metadata.Update.assert_not_called()
        mock_image_metadata.AssignVectorId.assert_not_called()
        mock_image_metadata.UnassignVectorId.assert_not_called()
        mock_dependencies["repository"].Save.assert_called_once_with(mock_image_metadata)
        mock_dependencies["uow"].Commit.assert_called_once()
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleBothVectorIdAndRemoveVectorId_ShouldPrioritizeRemove(
        self, handler, mock_dependencies, mock_image_metadata
    ):
        """Test that removeVectorId takes priority over vectorId assignment."""
        # Arrange
        image_id = ImageMetadataId(id=123)
        command = UpdateImageMetadataCommand(
            title=None,
            subtitle=None,
            description=None,
            vectorId=789,
            removeVectorId=True,
        )
        mock_image_metadata.vectorId = VectorId(id=456)  # Has vector ID
        mock_dependencies["repository"].FindById.return_value = mock_image_metadata

        # Act
        await handler.Handle(image_id, command)

        # Assert
        mock_image_metadata.UnassignVectorId.assert_called_once()
        mock_image_metadata.AssignVectorId.assert_not_called()
        mock_dependencies["repository"].Save.assert_called_once_with(mock_image_metadata)
        mock_dependencies["uow"].Commit.assert_called_once()
        mock_dependencies["event_dispatcher"].DispatchAll.assert_called_once()
