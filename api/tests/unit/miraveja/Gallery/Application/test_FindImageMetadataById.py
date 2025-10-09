import pytest
from typing import Any
from unittest.mock import MagicMock, Mock
from pydantic import ValidationError

from Miraveja.Gallery.Application.FindImageMetadataById import FindImageMetadataByIdHandler
from Miraveja.Gallery.Domain.Exceptions import ImageMetadataNotFoundException
from Miraveja.Gallery.Domain.Models import ImageMetadata, Size
from Miraveja.Gallery.Domain.Enums import ImageRepositoryType
from Miraveja.Shared.Identifiers.Models import ImageMetadataId, MemberId


class TestFindImageMetadataByIdHandler:
    """Test cases for FindImageMetadataByIdHandler application service."""

    def test_HandleWithExistingImageMetadata_ShouldReturnImageData(self):
        """Test that Handle returns image data when image metadata exists."""
        # Arrange
        image_id = ImageMetadataId(id=1)
        mock_image_metadata = ImageMetadata(
            id=image_id,
            ownerId=MemberId.Generate(),
            title="Test Image",
            subtitle="Test Subtitle",
            description="Test description",
            size=Size(width=1920, height=1080),
            repositoryType=ImageRepositoryType.S3,
            uri="https://example.com/image.jpg",
            isAiGenerated=False,
            generationMetadata=None,
            vectorId=None,
        )

        mock_repository = Mock()
        mock_repository.FindById.return_value = mock_image_metadata

        mock_unit_of_work = Mock()
        mock_unit_of_work.GetRepository.return_value = mock_repository
        mock_unit_of_work.__enter__ = Mock(return_value=mock_unit_of_work)
        mock_unit_of_work.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock()
        mock_uow_factory.Create.return_value = mock_unit_of_work

        mock_logger = Mock()
        mock_repository_type: Any = Mock()

        handler = FindImageMetadataByIdHandler(
            databaseUOWFactory=mock_uow_factory, tImageMetadataRepository=mock_repository_type, logger=mock_logger
        )

        # Act
        result = handler.Handle(image_id)

        # Assert
        assert result is not None
        assert result == mock_image_metadata.model_dump()
        mock_uow_factory.Create.assert_called_once()
        mock_unit_of_work.GetRepository.assert_called_once_with(mock_repository_type)
        mock_repository.FindById.assert_called_once_with(image_id)
        mock_logger.Info.assert_called()

    def test_HandleWithNonExistentImageMetadata_ShouldRaiseNotFoundException(self):
        """Test that Handle raises exception when image metadata does not exist."""
        # Arrange
        image_id = ImageMetadataId(id=999)

        mock_repository = Mock()
        mock_repository.FindById.return_value = None

        mock_unit_of_work = Mock()
        mock_unit_of_work.GetRepository.return_value = mock_repository
        mock_unit_of_work.__enter__ = Mock(return_value=mock_unit_of_work)
        mock_unit_of_work.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock()
        mock_uow_factory.Create.return_value = mock_unit_of_work

        mock_logger = Mock()
        mock_repository_type: Any = Mock()

        handler = FindImageMetadataByIdHandler(
            databaseUOWFactory=mock_uow_factory, tImageMetadataRepository=mock_repository_type, logger=mock_logger
        )

        # Act & Assert
        with pytest.raises(ImageMetadataNotFoundException) as exc_info:
            handler.Handle(image_id)

        assert exc_info.value.details is not None
        assert exc_info.value.details["imageId"] == image_id
        mock_repository.FindById.assert_called_once_with(image_id)
        mock_logger.Warning.assert_called_once()

    def test_InitializeWithValidParameters_ShouldSetCorrectProperties(self):
        """Test that handler initializes correctly with valid parameters."""
        # Arrange
        mock_uow_factory = Mock()
        mock_repository_type: Any = Mock()
        mock_logger = Mock()

        # Act
        handler = FindImageMetadataByIdHandler(
            databaseUOWFactory=mock_uow_factory, tImageMetadataRepository=mock_repository_type, logger=mock_logger
        )

        # Assert
        assert handler._databaseUOWFactory == mock_uow_factory
        assert handler._tImageMetadataRepository == mock_repository_type
        assert handler._logger == mock_logger
