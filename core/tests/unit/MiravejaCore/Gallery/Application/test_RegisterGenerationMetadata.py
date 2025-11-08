import pytest
from unittest.mock import MagicMock, AsyncMock
from pydantic import ValidationError

from MiravejaCore.Gallery.Application.RegisterGenerationMetadata import (
    RegisterGenerationMetadataCommand,
    RegisterGenerationMetadataHandler,
)
from MiravejaCore.Gallery.Application.RegisterLoraMetadata import RegisterLoraMetadataCommand
from MiravejaCore.Gallery.Domain.Enums import SamplerType, SchedulerType, TechniqueType
from MiravejaCore.Gallery.Domain.Interfaces import IGenerationMetadataRepository, ILoraMetadataRepository
from MiravejaCore.Gallery.Domain.Models import GenerationMetadata, LoraMetadata, Size
from MiravejaCore.Shared.Identifiers.Models import GenerationMetadataId, ImageMetadataId, LoraMetadataId
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class TestRegisterGenerationMetadataCommand:
    """Test cases for RegisterGenerationMetadataCommand model."""

    def test_InitializeWithValidMinimalData_ShouldSetCorrectValues(self):
        """Test that RegisterGenerationMetadataCommand initializes with minimal valid data."""
        # Arrange & Act
        command = RegisterGenerationMetadataCommand(prompt="A beautiful sunset over mountains")

        # Assert
        assert command.prompt == "A beautiful sunset over mountains"
        assert command.negativePrompt is None
        assert command.seed is None
        assert command.model is None
        assert command.sampler is None
        assert command.scheduler is None
        assert command.steps is None
        assert command.cfgScale is None
        assert command.size is None
        assert command.loras is None
        assert command.techniques is None

    def test_InitializeWithValidCompleteData_ShouldSetCorrectValues(self):
        """Test that RegisterGenerationMetadataCommand initializes with complete valid data."""
        # Arrange
        loras = [RegisterLoraMetadataCommand(hash="abc123", name="StyleLoRA")]
        size = Size(width=512, height=768)

        # Act
        command = RegisterGenerationMetadataCommand(
            prompt="A beautiful landscape",
            negativePrompt="ugly, blurry",
            seed="42",
            model="model_hash_123",
            sampler=SamplerType.EULER_A,
            scheduler=SchedulerType.KARRAS,
            steps=20,
            cfgScale=7.5,
            size=size,
            loras=loras,
            techniques=[TechniqueType.TEXT_TO_IMAGE],
        )

        # Assert
        assert command.prompt == "A beautiful landscape"
        assert command.negativePrompt == "ugly, blurry"
        assert command.seed == "42"
        assert command.model == "model_hash_123"
        assert command.sampler == SamplerType.EULER_A
        assert command.scheduler == SchedulerType.KARRAS
        assert command.steps == 20
        assert command.cfgScale == 7.5
        assert command.size == size
        assert len(command.loras) == 1
        assert command.loras[0].hash == "abc123"
        assert command.techniques == [TechniqueType.TEXT_TO_IMAGE]

    def test_InitializeWithPromptTooLong_ShouldRaiseValidationError(self):
        """Test that RegisterGenerationMetadataCommand raises validation error when prompt exceeds max length."""
        # Arrange
        longPrompt = "x" * 2001

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegisterGenerationMetadataCommand(prompt=longPrompt)

        assert "prompt" in str(exc_info.value)

    def test_InitializeWithNegativePromptTooLong_ShouldRaiseValidationError(self):
        """Test that RegisterGenerationMetadataCommand raises validation error when negative prompt exceeds max length."""
        # Arrange
        longNegativePrompt = "x" * 2001

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegisterGenerationMetadataCommand(prompt="valid prompt", negativePrompt=longNegativePrompt)

        assert "negativePrompt" in str(exc_info.value)

    def test_ValidateTechniquesWithCommaSeparatedString_ShouldConvertToList(self):
        """Test that techniques validator converts comma-separated string to list of TechniqueType."""
        # Arrange & Act
        command = RegisterGenerationMetadataCommand(
            prompt="Test prompt", techniques="txt2img,hires_fix,adetailer"  # type: ignore
        )

        # Assert
        assert isinstance(command.techniques, list)
        assert len(command.techniques) == 3
        assert command.techniques[0] == TechniqueType.TEXT_TO_IMAGE
        assert command.techniques[1] == TechniqueType.HIRES_FIX
        assert command.techniques[2] == TechniqueType.ADETAILER

    def test_ValidateTechniquesWithNone_ShouldReturnNone(self):
        """Test that techniques validator returns None when input is None."""
        # Arrange & Act
        command = RegisterGenerationMetadataCommand(prompt="Test prompt", techniques=None)

        # Assert
        assert command.techniques is None

    def test_ValidateTechniquesWithList_ShouldReturnList(self):
        """Test that techniques validator returns list when input is already a list."""
        # Arrange & Act
        command = RegisterGenerationMetadataCommand(
            prompt="Test prompt", techniques=[TechniqueType.TEXT_TO_IMAGE, TechniqueType.IMAGE_TO_IMAGE]
        )

        # Assert
        assert isinstance(command.techniques, list)
        assert len(command.techniques) == 2
        assert command.techniques[0] == TechniqueType.TEXT_TO_IMAGE
        assert command.techniques[1] == TechniqueType.IMAGE_TO_IMAGE


class TestRegisterGenerationMetadataHandler:
    """Test cases for RegisterGenerationMetadataHandler."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for RegisterGenerationMetadataHandler."""
        mockDatabaseManagerFactory = MagicMock()
        mockDatabaseManager = MagicMock()
        mockDatabaseManagerFactory.Create.return_value.__enter__ = MagicMock(return_value=mockDatabaseManager)
        mockDatabaseManagerFactory.Create.return_value.__exit__ = MagicMock(return_value=None)

        mockGenerationMetadataRepository = MagicMock(spec=IGenerationMetadataRepository)
        mockGenerationMetadataId = GenerationMetadataId(id=100)
        mockGenerationMetadataRepository.GenerateNewId.return_value = mockGenerationMetadataId
        mockDatabaseManager.GetRepository.return_value = mockGenerationMetadataRepository

        mockFindLoraMetadataByHashHandler = MagicMock()
        mockRegisterLoraMetadataHandler = MagicMock()
        mockLogger = MagicMock(spec=ILogger)

        return {
            "database_manager_factory": mockDatabaseManagerFactory,
            "database_manager": mockDatabaseManager,
            "generation_metadata_repository": mockGenerationMetadataRepository,
            "generation_metadata_id": mockGenerationMetadataId,
            "find_lora_metadata_handler": mockFindLoraMetadataByHashHandler,
            "register_lora_metadata_handler": mockRegisterLoraMetadataHandler,
            "logger": mockLogger,
        }

    def test_HandleWithMinimalCommand_ShouldRegisterGenerationMetadata(self, mock_dependencies):
        """Test that Handle registers generation metadata with minimal command data."""
        # Arrange
        handler = RegisterGenerationMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tGenerationMetadataRepository=IGenerationMetadataRepository,
            findLoraMetadataByHashHandler=mock_dependencies["find_lora_metadata_handler"],
            registerLoraMetadataHandler=mock_dependencies["register_lora_metadata_handler"],
            logger=mock_dependencies["logger"],
        )

        imageId = ImageMetadataId(id=42)
        command = RegisterGenerationMetadataCommand(prompt="A beautiful landscape")

        # Act
        result = handler.Handle(imageId, command)

        # Assert
        assert result == 100
        mock_dependencies["logger"].Info.assert_called()
        mock_dependencies["generation_metadata_repository"].Save.assert_called_once()
        mock_dependencies["database_manager"].Commit.assert_called_once()

        # Verify the saved generation metadata
        savedMetadata = mock_dependencies["generation_metadata_repository"].Save.call_args[0][0]
        assert isinstance(savedMetadata, GenerationMetadata)
        assert savedMetadata.id.id == 100
        assert savedMetadata.imageId.id == 42
        assert savedMetadata.prompt == "A beautiful landscape"
        assert savedMetadata.negativePrompt is None
        assert savedMetadata.loras is None or savedMetadata.loras == []

    def test_HandleWithCompleteCommandNoLoras_ShouldRegisterGenerationMetadataWithAllFields(self, mock_dependencies):
        """Test that Handle registers generation metadata with complete command data without LoRAs."""
        # Arrange
        handler = RegisterGenerationMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tGenerationMetadataRepository=IGenerationMetadataRepository,
            findLoraMetadataByHashHandler=mock_dependencies["find_lora_metadata_handler"],
            registerLoraMetadataHandler=mock_dependencies["register_lora_metadata_handler"],
            logger=mock_dependencies["logger"],
        )

        imageId = ImageMetadataId(id=42)
        size = Size(width=512, height=768)
        command = RegisterGenerationMetadataCommand(
            prompt="A beautiful landscape",
            negativePrompt="ugly, blurry",
            seed="12345",
            model="model_hash_xyz",
            sampler=SamplerType.EULER_A,
            scheduler=SchedulerType.KARRAS,
            steps=30,
            cfgScale=8.0,
            size=size,
            techniques=[TechniqueType.TEXT_TO_IMAGE, TechniqueType.HIRES_FIX],
        )

        # Act
        result = handler.Handle(imageId, command)

        # Assert
        assert result == 100
        mock_dependencies["generation_metadata_repository"].Save.assert_called_once()

        savedMetadata = mock_dependencies["generation_metadata_repository"].Save.call_args[0][0]
        assert savedMetadata.prompt == "A beautiful landscape"
        assert savedMetadata.negativePrompt == "ugly, blurry"
        assert savedMetadata.seed == "12345"
        assert savedMetadata.model == "model_hash_xyz"
        assert savedMetadata.sampler == SamplerType.EULER_A
        assert savedMetadata.scheduler == SchedulerType.KARRAS
        assert savedMetadata.steps == 30
        assert savedMetadata.cfgScale == 8.0
        assert savedMetadata.size == size
        assert savedMetadata.techniques == [TechniqueType.TEXT_TO_IMAGE, TechniqueType.HIRES_FIX]

    def test_HandleWithExistingLoras_ShouldReuseExistingLoraMetadata(self, mock_dependencies):
        """Test that Handle reuses existing LoRA metadata when LoRA already exists."""
        # Arrange
        handler = RegisterGenerationMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tGenerationMetadataRepository=IGenerationMetadataRepository,
            findLoraMetadataByHashHandler=mock_dependencies["find_lora_metadata_handler"],
            registerLoraMetadataHandler=mock_dependencies["register_lora_metadata_handler"],
            logger=mock_dependencies["logger"],
        )

        # Mock existing LoRA
        existingLoraData = {"id": 50, "hash": "lora_hash_123", "name": "ExistingLoRA"}
        mock_dependencies["find_lora_metadata_handler"].Handle.return_value = existingLoraData

        imageId = ImageMetadataId(id=42)
        loraCommand = RegisterLoraMetadataCommand(hash="lora_hash_123", name="ExistingLoRA")
        command = RegisterGenerationMetadataCommand(prompt="Test prompt", loras=[loraCommand])

        # Act
        result = handler.Handle(imageId, command)

        # Assert
        assert result == 100
        mock_dependencies["find_lora_metadata_handler"].Handle.assert_called_once_with("lora_hash_123")
        mock_dependencies["register_lora_metadata_handler"].Handle.assert_not_called()
        mock_dependencies["logger"].Debug.assert_any_call("LoRA with hash lora_hash_123 already exists with ID 50")

        savedMetadata = mock_dependencies["generation_metadata_repository"].Save.call_args[0][0]
        assert len(savedMetadata.loras) == 1
        assert savedMetadata.loras[0].id.id == 50
        assert savedMetadata.loras[0].hash == "lora_hash_123"

    def test_HandleWithNewLoras_ShouldRegisterNewLoraMetadata(self, mock_dependencies):
        """Test that Handle registers new LoRA metadata when LoRA doesn't exist."""
        # Arrange
        handler = RegisterGenerationMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tGenerationMetadataRepository=IGenerationMetadataRepository,
            findLoraMetadataByHashHandler=mock_dependencies["find_lora_metadata_handler"],
            registerLoraMetadataHandler=mock_dependencies["register_lora_metadata_handler"],
            logger=mock_dependencies["logger"],
        )

        # Mock new LoRA (not found)
        mock_dependencies["find_lora_metadata_handler"].Handle.return_value = None
        mock_dependencies["register_lora_metadata_handler"].Handle.return_value = 60

        imageId = ImageMetadataId(id=42)
        loraCommand = RegisterLoraMetadataCommand(hash="new_lora_hash", name="NewLoRA")
        command = RegisterGenerationMetadataCommand(prompt="Test prompt", loras=[loraCommand])

        # Act
        result = handler.Handle(imageId, command)

        # Assert
        assert result == 100
        mock_dependencies["find_lora_metadata_handler"].Handle.assert_called_once_with("new_lora_hash")
        mock_dependencies["register_lora_metadata_handler"].Handle.assert_called_once_with(loraCommand)
        mock_dependencies["logger"].Debug.assert_any_call("Registered new LoRA with hash new_lora_hash and ID 60")

        savedMetadata = mock_dependencies["generation_metadata_repository"].Save.call_args[0][0]
        assert len(savedMetadata.loras) == 1
        assert savedMetadata.loras[0].id.id == 60
        assert savedMetadata.loras[0].hash == "new_lora_hash"
        assert savedMetadata.loras[0].name == "NewLoRA"

    def test_HandleWithMultipleMixedLoras_ShouldHandleBothExistingAndNewLoras(self, mock_dependencies):
        """Test that Handle correctly handles a mix of existing and new LoRAs."""
        # Arrange
        handler = RegisterGenerationMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tGenerationMetadataRepository=IGenerationMetadataRepository,
            findLoraMetadataByHashHandler=mock_dependencies["find_lora_metadata_handler"],
            registerLoraMetadataHandler=mock_dependencies["register_lora_metadata_handler"],
            logger=mock_dependencies["logger"],
        )

        # Mock first LoRA exists, second is new
        existingLoraData = {"id": 70, "hash": "existing_hash", "name": "ExistingLoRA"}

        def find_lora_side_effect(hash_value):
            if hash_value == "existing_hash":
                return existingLoraData
            return None

        mock_dependencies["find_lora_metadata_handler"].Handle.side_effect = find_lora_side_effect
        mock_dependencies["register_lora_metadata_handler"].Handle.return_value = 80

        imageId = ImageMetadataId(id=42)
        lora1 = RegisterLoraMetadataCommand(hash="existing_hash", name="ExistingLoRA")
        lora2 = RegisterLoraMetadataCommand(hash="new_hash", name="NewLoRA")
        command = RegisterGenerationMetadataCommand(prompt="Test prompt", loras=[lora1, lora2])

        # Act
        result = handler.Handle(imageId, command)

        # Assert
        assert result == 100
        assert mock_dependencies["find_lora_metadata_handler"].Handle.call_count == 2
        mock_dependencies["register_lora_metadata_handler"].Handle.assert_called_once_with(lora2)

        savedMetadata = mock_dependencies["generation_metadata_repository"].Save.call_args[0][0]
        assert len(savedMetadata.loras) == 2
        assert savedMetadata.loras[0].id.id == 70
        assert savedMetadata.loras[0].hash == "existing_hash"
        assert savedMetadata.loras[1].id.id == 80
        assert savedMetadata.loras[1].hash == "new_hash"

    def test_HandleWithNoLoras_ShouldNotCallLoraHandlers(self, mock_dependencies):
        """Test that Handle doesn't call LoRA handlers when no LoRAs are provided."""
        # Arrange
        handler = RegisterGenerationMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tGenerationMetadataRepository=IGenerationMetadataRepository,
            findLoraMetadataByHashHandler=mock_dependencies["find_lora_metadata_handler"],
            registerLoraMetadataHandler=mock_dependencies["register_lora_metadata_handler"],
            logger=mock_dependencies["logger"],
        )

        imageId = ImageMetadataId(id=42)
        command = RegisterGenerationMetadataCommand(prompt="Test prompt", loras=None)

        # Act
        result = handler.Handle(imageId, command)

        # Assert
        assert result == 100
        mock_dependencies["find_lora_metadata_handler"].Handle.assert_not_called()
        mock_dependencies["register_lora_metadata_handler"].Handle.assert_not_called()

        savedMetadata = mock_dependencies["generation_metadata_repository"].Save.call_args[0][0]
        assert savedMetadata.loras == []

    def test_HandleWithEmptyLorasList_ShouldNotCallLoraHandlers(self, mock_dependencies):
        """Test that Handle doesn't call LoRA handlers when LoRAs list is empty."""
        # Arrange
        handler = RegisterGenerationMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tGenerationMetadataRepository=IGenerationMetadataRepository,
            findLoraMetadataByHashHandler=mock_dependencies["find_lora_metadata_handler"],
            registerLoraMetadataHandler=mock_dependencies["register_lora_metadata_handler"],
            logger=mock_dependencies["logger"],
        )

        imageId = ImageMetadataId(id=42)
        command = RegisterGenerationMetadataCommand(prompt="Test prompt", loras=[])

        # Act
        result = handler.Handle(imageId, command)

        # Assert
        assert result == 100
        mock_dependencies["find_lora_metadata_handler"].Handle.assert_not_called()
        mock_dependencies["register_lora_metadata_handler"].Handle.assert_not_called()

        savedMetadata = mock_dependencies["generation_metadata_repository"].Save.call_args[0][0]
        assert savedMetadata.loras == []

    def test_HandleLogsCorrectly_ShouldCallLoggerMethods(self, mock_dependencies):
        """Test that Handle logs appropriate information during execution."""
        # Arrange
        handler = RegisterGenerationMetadataHandler(
            databaseManagerFactory=mock_dependencies["database_manager_factory"],
            tGenerationMetadataRepository=IGenerationMetadataRepository,
            findLoraMetadataByHashHandler=mock_dependencies["find_lora_metadata_handler"],
            registerLoraMetadataHandler=mock_dependencies["register_lora_metadata_handler"],
            logger=mock_dependencies["logger"],
        )

        imageId = ImageMetadataId(id=42)
        command = RegisterGenerationMetadataCommand(prompt="Test prompt")

        # Act
        result = handler.Handle(imageId, command)

        # Assert
        assert result == 100
        assert mock_dependencies["logger"].Info.call_count >= 2  # Start and end logging
        assert mock_dependencies["logger"].Debug.call_count >= 1  # Debug logging for entity creation
        mock_dependencies["logger"].Info.assert_any_call("Generation metadata registered with ID: 100")
