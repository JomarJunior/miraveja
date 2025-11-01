import pytest
from unittest.mock import MagicMock, Mock
from typing import Type

from MiravejaApi.Gallery.Application.FindLoraMetadataByHash import FindLoraMetadataByHashHandler
from MiravejaApi.Gallery.Domain.Interfaces import ILoraMetadataRepository
from MiravejaApi.Gallery.Domain.Models import LoraMetadata
from MiravejaApi.Shared.Identifiers.Models import LoraMetadataId
from MiravejaApi.Shared.Logging.Interfaces import ILogger
from MiravejaApi.Shared.databaseManager.Domain.Interfaces import IDatabaseManagerFactory, IDatabaseManager
from MiravejaApi.Shared.Utils.Types.Handler import HandlerResponse


class TestFindLoraMetadataByHashHandler:
    """Test cases for FindLoraMetadataByHashHandler application service."""

    def test_InitializeWithValidDependencies_ShouldSetCorrectProperties(self):
        """Test that FindLoraMetadataByHashHandler initializes with valid dependencies."""
        # Arrange
        mock_uow_factory = Mock(spec=IDatabaseManagerFactory)
        mock_repository_type = ILoraMetadataRepository
        mock_logger = Mock(spec=ILogger)

        # Act
        handler = FindLoraMetadataByHashHandler(mock_uow_factory, mock_repository_type, mock_logger)

        # Assert
        assert handler._databaseManagerFactory == mock_uow_factory
        assert handler._tLoraMetadataRepository == mock_repository_type
        assert handler._logger == mock_logger

    def test_HandleWithExistingLora_ShouldReturnLoraResponse(self):
        """Test that Handle returns lora when lora exists."""
        # Arrange
        test_hash = "abcd1234hash"
        lora_id = LoraMetadataId(id=1)
        lora = LoraMetadata.Register(id=lora_id, hash=test_hash, name="Test Lora")

        mock_uow = Mock(spec=IDatabaseManager)
        mock_repository = Mock(spec=ILoraMetadataRepository)
        mock_repository.FindByHash.return_value = lora
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IDatabaseManagerFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = ILoraMetadataRepository
        mock_logger = Mock(spec=ILogger)

        handler = FindLoraMetadataByHashHandler(mock_uow_factory, mock_repository_type, mock_logger)

        # Act
        result = handler.Handle(test_hash)

        # Assert
        assert result is not None
        mock_logger.Info.assert_called()
        mock_repository.FindByHash.assert_called_once_with(test_hash)

    def test_HandleWithNonExistingLora_ShouldReturnNone(self):
        """Test that Handle returns None when lora does not exist."""
        # Arrange
        test_hash = "nonexistenthash"

        mock_uow = Mock(spec=IDatabaseManager)
        mock_repository = Mock(spec=ILoraMetadataRepository)
        mock_repository.FindByHash.return_value = None
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IDatabaseManagerFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = ILoraMetadataRepository
        mock_logger = Mock(spec=ILogger)

        handler = FindLoraMetadataByHashHandler(mock_uow_factory, mock_repository_type, mock_logger)

        # Act
        result = handler.Handle(test_hash)

        # Assert
        assert result is None
        mock_repository.FindByHash.assert_called_once_with(test_hash)

    def test_HandleWithValidHash_ShouldLogInfoMessage(self):
        """Test that Handle logs info message with hash parameter."""
        # Arrange
        test_hash = "testhash"

        mock_uow = Mock(spec=IDatabaseManager)
        mock_repository = Mock(spec=ILoraMetadataRepository)
        mock_repository.FindByHash.return_value = None
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IDatabaseManagerFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = ILoraMetadataRepository
        mock_logger = Mock(spec=ILogger)

        handler = FindLoraMetadataByHashHandler(mock_uow_factory, mock_repository_type, mock_logger)

        # Act
        handler.Handle(test_hash)

        # Assert
        assert mock_logger.Info.call_count >= 1
        logged_message = mock_logger.Info.call_args_list[0][0][0]
        assert "Finding LoRA metadata by hash:" in logged_message
