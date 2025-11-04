import pytest
from typing import Any
from unittest.mock import MagicMock, Mock

from MiravejaCore.Gallery.Application.ListAllImageMetadatas import (
    ListAllImageMetadatasHandler,
    ListAllImageMetadatasCommand,
)
from MiravejaCore.Gallery.Domain.Models import ImageMetadata, Size
from MiravejaCore.Gallery.Domain.Enums import ImageRepositoryType
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId, MemberId


class TestListAllImageMetadatasHandler:
    """Test cases for ListAllImageMetadatasHandler application service."""

    def test_HandleWithExistingImageMetadatas_ShouldReturnPaginatedResult(self):
        """Test that Handle returns paginated results when image metadatas exist."""
        # Arrange
        mock_image_metadata_1 = ImageMetadata(
            id=ImageMetadataId(id=1),
            ownerId=MemberId.Generate(),
            title="Test Image 1",
            subtitle="Test Subtitle 1",
            description="Test description 1",
            size=Size(width=1920, height=1080),
            repositoryType=ImageRepositoryType.S3,
            uri="https://example.com/image1.jpg",
            isAiGenerated=False,
            generationMetadata=None,
            vectorId=None,
        )

        mock_image_metadata_2 = ImageMetadata(
            id=ImageMetadataId(id=2),
            ownerId=MemberId.Generate(),
            title="Test Image 2",
            subtitle="Test Subtitle 2",
            description="Test description 2",
            size=Size(width=512, height=512),
            repositoryType=ImageRepositoryType.DISK,
            uri="https://example.com/image2.jpg",
            isAiGenerated=True,
            generationMetadata=None,
            vectorId=None,
        )

        mock_image_metadatas = [mock_image_metadata_1, mock_image_metadata_2]

        mock_repository = Mock()
        mock_repository.ListAll.return_value = mock_image_metadatas
        mock_repository.Count.return_value = 2

        mock_unit_of_work = Mock()
        mock_unit_of_work.GetRepository.return_value = mock_repository
        mock_unit_of_work.__enter__ = Mock(return_value=mock_unit_of_work)
        mock_unit_of_work.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock()
        mock_uow_factory.Create.return_value = mock_unit_of_work

        mock_logger = Mock()
        mock_repository_type: Any = Mock()

        handler = ListAllImageMetadatasHandler(
            databaseManagerFactory=mock_uow_factory, tImageMetadataRepository=mock_repository_type, logger=mock_logger
        )

        command = ListAllImageMetadatasCommand()

        # Act
        result = handler.Handle(command)

        # Assert
        assert result is not None
        assert "items" in result
        assert "pagination" in result
        assert len(result["items"]) == 2
        assert result["pagination"]["total"] == 2
        assert result["items"][0] == mock_image_metadata_1.model_dump()
        assert result["items"][1] == mock_image_metadata_2.model_dump()

        mock_uow_factory.Create.assert_called_once()
        mock_unit_of_work.GetRepository.assert_called_once_with(mock_repository_type)
        mock_repository.ListAll.assert_called_once_with(command)
        mock_repository.Count.assert_called_once()
        mock_logger.Info.assert_called()

    def test_HandleWithNoImageMetadatas_ShouldReturnEmptyResult(self):
        """Test that Handle returns empty results when no image metadatas exist."""
        # Arrange
        mock_repository = Mock()
        mock_repository.ListAll.return_value = []
        mock_repository.Count.return_value = 0

        mock_unit_of_work = Mock()
        mock_unit_of_work.GetRepository.return_value = mock_repository
        mock_unit_of_work.__enter__ = Mock(return_value=mock_unit_of_work)
        mock_unit_of_work.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock()
        mock_uow_factory.Create.return_value = mock_unit_of_work

        mock_logger = Mock()
        mock_repository_type: Any = Mock()

        handler = ListAllImageMetadatasHandler(
            databaseManagerFactory=mock_uow_factory, tImageMetadataRepository=mock_repository_type, logger=mock_logger
        )

        command = ListAllImageMetadatasCommand()

        # Act
        result = handler.Handle(command)

        # Assert
        assert result is not None
        assert "items" in result
        assert "pagination" in result
        assert len(result["items"]) == 0
        assert result["pagination"]["total"] == 0

        mock_repository.ListAll.assert_called_once_with(command)
        mock_repository.Count.assert_called_once()

    def test_InitializeWithValidParameters_ShouldSetCorrectProperties(self):
        """Test that handler initializes correctly with valid parameters."""
        # Arrange
        mock_uow_factory = Mock()
        mock_repository_type: Any = Mock()
        mock_logger = Mock()

        # Act
        handler = ListAllImageMetadatasHandler(
            databaseManagerFactory=mock_uow_factory, tImageMetadataRepository=mock_repository_type, logger=mock_logger
        )

        # Assert
        assert handler._databaseManagerFactory == mock_uow_factory
        assert handler._tImageMetadataRepository == mock_repository_type
        assert handler._logger == mock_logger


class TestListAllImageMetadatasCommand:
    """Test cases for ListAllImageMetadatasCommand."""

    def test_InitializeWithDefaultValues_ShouldInheritFromListAllQuery(self):
        """Test that command initializes with default values from ListAllQuery."""
        # Act
        command = ListAllImageMetadatasCommand()

        # Assert
        assert hasattr(command, "offset")
        assert hasattr(command, "limit")
        assert hasattr(command, "sortBy")
        assert hasattr(command, "sortOrder")
