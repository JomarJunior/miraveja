import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError

from MiravejaCore.Gallery.Application.RegisterLoraMetadata import (
    RegisterLoraMetadataCommand,
    RegisterLoraMetadataHandler,
)
from MiravejaCore.Gallery.Domain.Interfaces import ILoraMetadataRepository
from MiravejaCore.Gallery.Domain.Models import LoraMetadata
from MiravejaCore.Shared.Identifiers.Models import LoraMetadataId
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class TestRegisterLoraMetadataCommand:
    """Test cases for RegisterLoraMetadataCommand model."""

    def test_InitializeWithHashOnly_ShouldSetCorrectValues(self):
        """Test that RegisterLoraMetadataCommand initializes with hash only."""
        # Arrange & Act
        command = RegisterLoraMetadataCommand(hash="abc123hash")

        # Assert
        assert command.hash == "abc123hash"
        assert command.name is None

    def test_InitializeWithHashAndName_ShouldSetCorrectValues(self):
        """Test that RegisterLoraMetadataCommand initializes with hash and name."""
        # Arrange & Act
        command = RegisterLoraMetadataCommand(hash="xyz789hash", name="StyleLoRA")

        # Assert
        assert command.hash == "xyz789hash"
        assert command.name == "StyleLoRA"

    def test_InitializeWithoutHash_ShouldRaiseValidationError(self):
        """Test that RegisterLoraMetadataCommand raises validation error without hash."""
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegisterLoraMetadataCommand()  # type: ignore

        assert "hash" in str(exc_info.value)


class TestRegisterLoraMetadataHandler:
    """Test cases for RegisterLoraMetadataHandler."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for RegisterLoraMetadataHandler."""
        mockDatabaseManagerFactory = MagicMock()
        mockDatabaseManager = MagicMock()
        mockDatabaseManagerFactory.Create.return_value.__enter__ = MagicMock(return_value=mockDatabaseManager)
        mockDatabaseManagerFactory.Create.return_value.__exit__ = MagicMock(return_value=None)

        mockLoraMetadataRepository = MagicMock(spec=ILoraMetadataRepository)
        mockLoraMetadataId = LoraMetadataId(id=42)
        mockLoraMetadataRepository.GenerateNewId.return_value = mockLoraMetadataId
        mockDatabaseManager.GetRepository.return_value = mockLoraMetadataRepository

        mockLogger = MagicMock(spec=ILogger)

        return {
            "database_manager_factory": mockDatabaseManagerFactory,
            "database_manager": mockDatabaseManager,
            "lora_metadata_repository": mockLoraMetadataRepository,
            "lora_metadata_id": mockLoraMetadataId,
            "logger": mockLogger,
        }

    def test_HandleWithHashOnly_ShouldRegisterLoraMetadata(self, mock_dependencies):
        """Test that Handle registers LoRA metadata with hash only."""
        # Arrange
        handler = RegisterLoraMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tLoraMetadataRepository=ILoraMetadataRepository,
            logger=mock_dependencies["logger"],
        )

        command = RegisterLoraMetadataCommand(hash="test_hash_123")

        # Act
        result = handler.Handle(command)

        # Assert
        assert result == 42
        mock_dependencies["logger"].Info.assert_called()
        # The log message includes the object representation (e.g., "id=42")
        debugCallArgs = mock_dependencies["logger"].Debug.call_args[0][0]
        assert "Creating LoRA metadata entity with ID:" in debugCallArgs
        assert "42" in debugCallArgs
        mock_dependencies["lora_metadata_repository"].Save.assert_called_once()
        mock_dependencies["database_manager"].Commit.assert_called_once()

        # Verify the saved LoRA metadata
        savedMetadata = mock_dependencies["lora_metadata_repository"].Save.call_args[0][0]
        assert isinstance(savedMetadata, LoraMetadata)
        assert savedMetadata.id.id == 42
        assert savedMetadata.hash == "test_hash_123"
        assert savedMetadata.name is None

    def test_HandleWithHashAndName_ShouldRegisterLoraMetadataWithName(self, mock_dependencies):
        """Test that Handle registers LoRA metadata with hash and name."""
        # Arrange
        handler = RegisterLoraMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tLoraMetadataRepository=ILoraMetadataRepository,
            logger=mock_dependencies["logger"],
        )

        command = RegisterLoraMetadataCommand(hash="test_hash_456", name="CustomStyleLoRA")

        # Act
        result = handler.Handle(command)

        # Assert
        assert result == 42
        mock_dependencies["lora_metadata_repository"].Save.assert_called_once()

        savedMetadata = mock_dependencies["lora_metadata_repository"].Save.call_args[0][0]
        assert savedMetadata.hash == "test_hash_456"
        assert savedMetadata.name == "CustomStyleLoRA"

    def test_HandleLogsCorrectly_ShouldCallLoggerMethods(self, mock_dependencies):
        """Test that Handle logs appropriate information during execution."""
        # Arrange
        handler = RegisterLoraMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tLoraMetadataRepository=ILoraMetadataRepository,
            logger=mock_dependencies["logger"],
        )

        command = RegisterLoraMetadataCommand(hash="test_hash_789")

        # Act
        result = handler.Handle(command)

        # Assert
        assert result == 42
        assert mock_dependencies["logger"].Info.call_count == 2  # Start and end logging
        mock_dependencies["logger"].Debug.assert_called_once()

        # Check specific log messages
        infoCallArgs = [call[0][0] for call in mock_dependencies["logger"].Info.call_args_list]
        assert any("Registering LoRA metadata with command" in msg for msg in infoCallArgs)
        # The final log message includes the object representation, just check for the key parts
        assert any("LoRA metadata registered with ID:" in msg and "42" in msg for msg in infoCallArgs)

    def test_HandleUsesCorrectRepository_ShouldCallGetRepository(self, mock_dependencies):
        """Test that Handle uses the correct repository from database manager."""
        # Arrange
        handler = RegisterLoraMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tLoraMetadataRepository=ILoraMetadataRepository,
            logger=mock_dependencies["logger"],
        )

        command = RegisterLoraMetadataCommand(hash="test_hash_999")

        # Act
        result = handler.Handle(command)

        # Assert
        assert result == 42
        # Verify GetRepository was called twice (once for GenerateNewId, once for Save)
        assert mock_dependencies["database_manager"].GetRepository.call_count == 2
        mock_dependencies["database_manager"].GetRepository.assert_called_with(ILoraMetadataRepository)

    def test_HandleCommitsTransaction_ShouldCallCommit(self, mock_dependencies):
        """Test that Handle commits the transaction after saving."""
        # Arrange
        handler = RegisterLoraMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tLoraMetadataRepository=ILoraMetadataRepository,
            logger=mock_dependencies["logger"],
        )

        command = RegisterLoraMetadataCommand(hash="test_hash_commit")

        # Act
        result = handler.Handle(command)

        # Assert
        assert result == 42
        mock_dependencies["database_manager"].Commit.assert_called_once()

        # Verify Commit is called after Save
        saveCallOrder = mock_dependencies["lora_metadata_repository"].Save.call_count
        commitCallOrder = mock_dependencies["database_manager"].Commit.call_count
        assert saveCallOrder > 0
        assert commitCallOrder > 0
