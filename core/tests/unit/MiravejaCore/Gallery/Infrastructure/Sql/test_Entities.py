import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from MiravejaCore.Gallery.Infrastructure.Sql.Entities import (
    Base,
    LoraMetaToGenerationMetaEntity,
    LoraMetadataEntity,
    GenerationMetadataEntity,
    ImageMetadataEntity,
)
from MiravejaCore.Gallery.Domain.Enums import SamplerType, SchedulerType


class TestLoraMetaToGenerationMetaEntity:
    """Test cases for LoraMetaToGenerationMetaEntity model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that LoraMetaToGenerationMetaEntity initializes with valid data."""
        # Arrange & Act
        entity = LoraMetaToGenerationMetaEntity()
        entity.id = 1
        entity.loraId = 10
        entity.generationMetadataId = 20

        # Assert
        assert entity.id == 1
        assert entity.loraId == 10
        assert entity.generationMetadataId == 20

    def test_ToDictWithValidData_ShouldReturnCorrectDictionary(self):
        """Test that ToDict returns correct dictionary representation."""
        # Arrange
        entity = LoraMetaToGenerationMetaEntity()
        entity.id = 5
        entity.loraId = 15
        entity.generationMetadataId = 25

        # Act
        result = entity.ToDict()

        # Assert
        assert result == {
            "id": 5,
            "loraId": 15,
            "generationMetadataId": 25,
        }


class TestLoraMetadataEntity:
    """Test cases for LoraMetadataEntity model."""

    def test_InitializeWithRequiredFields_ShouldSetCorrectValues(self):
        """Test that LoraMetadataEntity initializes with required fields."""
        # Arrange & Act
        entity = LoraMetadataEntity()
        entity.id = 1
        entity.hash = "abc123hash"
        entity.name = None

        # Assert
        assert entity.id == 1
        assert entity.hash == "abc123hash"
        assert entity.name is None

    def test_InitializeWithAllFields_ShouldSetCorrectValues(self):
        """Test that LoraMetadataEntity initializes with all fields."""
        # Arrange & Act
        entity = LoraMetadataEntity()
        entity.id = 2
        entity.hash = "xyz789hash"
        entity.name = "StyleLoRA"

        # Assert
        assert entity.id == 2
        assert entity.hash == "xyz789hash"
        assert entity.name == "StyleLoRA"

    def test_ToDictWithNoGenerationMetadatas_ShouldReturnEmptyList(self):
        """Test that ToDict returns empty list when no generation metadatas exist."""
        # Arrange
        entity = LoraMetadataEntity()
        entity.id = 3
        entity.hash = "test_hash"
        entity.name = "TestLoRA"
        entity.generationMetadatas = []

        # Act
        result = entity.ToDict()

        # Assert
        assert result == {
            "id": 3,
            "hash": "test_hash",
            "name": "TestLoRA",
            "generationMetadatas": [],
        }

    def test_ToDictWithGenerationMetadatas_ShouldReturnGenerationMetadataIds(self):
        """Test that ToDict returns list of generation metadata IDs."""
        # Arrange
        entity = LoraMetadataEntity()
        entity.id = 4
        entity.hash = "hash_with_gen"
        entity.name = "LoRAWithGen"

        # Mock generation metadata entities
        mockGen1 = MagicMock()
        mockGen1.id = 100
        mockGen2 = MagicMock()
        mockGen2.id = 200

        entity.generationMetadatas = [mockGen1, mockGen2]

        # Act
        result = entity.ToDict()

        # Assert
        assert result["id"] == 4
        assert result["hash"] == "hash_with_gen"
        assert result["name"] == "LoRAWithGen"
        assert result["generationMetadatas"] == [100, 200]

    def test_ToDictWithoutSettingGenerationMetadatas_ShouldHandleGracefully(self):
        """Test that ToDict handles uninitialized generationMetadatas gracefully."""
        # Arrange
        entity = LoraMetadataEntity()
        entity.id = 5
        entity.hash = "hash_none"
        entity.name = None
        # Don't set generationMetadatas at all - test the default behavior

        # Act
        result = entity.ToDict()

        # Assert
        # When relationship is not initialized, it should handle gracefully
        assert "generationMetadatas" in result


class TestGenerationMetadataEntity:
    """Test cases for GenerationMetadataEntity model."""

    def test_InitializeWithRequiredFields_ShouldSetCorrectValues(self):
        """Test that GenerationMetadataEntity initializes with required fields."""
        # Arrange & Act
        entity = GenerationMetadataEntity()
        entity.id = 1
        entity.imageId = 100
        entity.prompt = "A beautiful landscape"

        # Assert
        assert entity.id == 1
        assert entity.imageId == 100
        assert entity.prompt == "A beautiful landscape"

    def test_InitializeWithAllFields_ShouldSetCorrectValues(self):
        """Test that GenerationMetadataEntity initializes with all fields."""
        # Arrange & Act
        entity = GenerationMetadataEntity()
        entity.id = 2
        entity.imageId = 200
        entity.prompt = "A sunset"
        entity.negativePrompt = "ugly, blurry"
        entity.seed = "12345"
        entity.model = "model_hash"
        entity.sampler = SamplerType.EULER_A
        entity.scheduler = SchedulerType.KARRAS
        entity.steps = 30
        entity.cfgScale = 7.5
        entity.size = "512x768"
        entity.techniques = "txt2img,hires_fix"

        # Assert
        assert entity.id == 2
        assert entity.imageId == 200
        assert entity.prompt == "A sunset"
        assert entity.negativePrompt == "ugly, blurry"
        assert entity.seed == "12345"
        assert entity.model == "model_hash"
        assert entity.sampler == SamplerType.EULER_A
        assert entity.scheduler == SchedulerType.KARRAS
        assert entity.steps == 30
        assert entity.cfgScale == 7.5
        assert entity.size == "512x768"
        assert entity.techniques == "txt2img,hires_fix"

    def test_ToDictWithMinimalData_ShouldReturnCorrectDictionary(self):
        """Test that ToDict returns correct dictionary with minimal data."""
        # Arrange
        entity = GenerationMetadataEntity()
        entity.id = 3
        entity.imageId = 300
        entity.prompt = "Test prompt"
        entity.negativePrompt = None
        entity.seed = None
        entity.model = None
        entity.sampler = None
        entity.scheduler = None
        entity.steps = None
        entity.cfgScale = None
        entity.size = None
        entity.techniques = None
        entity.loras = []

        # Act
        result = entity.ToDict()

        # Assert
        assert result["id"] == 3
        assert result["imageId"] == 300
        assert result["prompt"] == "Test prompt"
        assert result["negativePrompt"] is None
        assert result["seed"] is None
        assert result["model"] is None
        assert result["sampler"] is None
        assert result["scheduler"] is None
        assert result["steps"] is None
        assert result["cfgScale"] is None
        assert result["size"] is None
        assert result["loras"] == []
        assert result["techniques"] is None

    def test_ToDictWithCompleteData_ShouldReturnCorrectDictionary(self):
        """Test that ToDict returns correct dictionary with complete data."""
        # Arrange
        entity = GenerationMetadataEntity()
        entity.id = 4
        entity.imageId = 400
        entity.prompt = "Complete prompt"
        entity.negativePrompt = "bad quality"
        entity.seed = "98765"
        entity.model = "complete_model"
        entity.sampler = SamplerType.DPMPP_2M
        entity.scheduler = SchedulerType.EXPONENTIAL
        entity.steps = 50
        entity.cfgScale = 9.0
        entity.size = "1024x1024"
        entity.techniques = "txt2img,adetailer,hires_fix"

        # Mock LoRA entities
        mockLora1 = MagicMock()
        mockLora1.ToDict.return_value = {"id": 10, "hash": "lora1", "name": "LoRA1"}
        mockLora2 = MagicMock()
        mockLora2.ToDict.return_value = {"id": 20, "hash": "lora2", "name": "LoRA2"}
        entity.loras = [mockLora1, mockLora2]

        # Act
        result = entity.ToDict()

        # Assert
        assert result["id"] == 4
        assert result["imageId"] == 400
        assert result["prompt"] == "Complete prompt"
        assert result["negativePrompt"] == "bad quality"
        assert result["seed"] == "98765"
        assert result["model"] == "complete_model"
        assert result["sampler"] == SamplerType.DPMPP_2M
        assert result["scheduler"] == SchedulerType.EXPONENTIAL
        assert result["steps"] == 50
        assert result["cfgScale"] == 9.0
        assert result["size"] == "1024x1024"
        assert len(result["loras"]) == 2
        assert result["loras"][0]["id"] == 10
        assert result["loras"][1]["id"] == 20
        assert result["techniques"] == ["txt2img", "adetailer", "hires_fix"]

    def test_ToDictWithTechniquesString_ShouldSplitIntoList(self):
        """Test that ToDict splits techniques string into list."""
        # Arrange
        entity = GenerationMetadataEntity()
        entity.id = 5
        entity.imageId = 500
        entity.prompt = "Test"
        entity.techniques = "txt2img,img2img,inpainting"
        entity.loras = []

        # Act
        result = entity.ToDict()

        # Assert
        assert result["techniques"] == ["txt2img", "img2img", "inpainting"]

    def test_ToDictWithNoneTechniques_ShouldReturnNone(self):
        """Test that ToDict returns None when techniques is None."""
        # Arrange
        entity = GenerationMetadataEntity()
        entity.id = 6
        entity.imageId = 600
        entity.prompt = "Test"
        entity.techniques = None
        entity.loras = []

        # Act
        result = entity.ToDict()

        # Assert
        assert result["techniques"] is None

    def test_ToDictWithEmptyTechniquesString_ShouldReturnNone(self):
        """Test that ToDict returns None for empty techniques string."""
        # Arrange
        entity = GenerationMetadataEntity()
        entity.id = 7
        entity.imageId = 700
        entity.prompt = "Test"
        entity.techniques = ""  # Empty string is falsy, so should return None
        entity.loras = []

        # Act
        result = entity.ToDict()

        # Assert
        assert result["techniques"] is None

    def test_ToDictWithEmptyLorasList_ShouldReturnEmptyList(self):
        """Test that ToDict handles empty loras list."""
        # Arrange
        entity = GenerationMetadataEntity()
        entity.id = 8
        entity.imageId = 800
        entity.prompt = "Test"
        entity.techniques = None
        entity.loras = []

        # Act
        result = entity.ToDict()

        # Assert
        assert result["loras"] == []


class TestImageMetadataEntity:
    """Test cases for ImageMetadataEntity model."""

    def test_InitializeWithRequiredFields_ShouldSetCorrectValues(self):
        """Test that ImageMetadataEntity initializes with required fields."""
        # Arrange
        now = datetime.now(timezone.utc)

        # Act
        entity = ImageMetadataEntity()
        entity.id = 1
        entity.ownerId = "owner-uuid-123"
        entity.title = "Test Image"
        entity.subtitle = "Test Subtitle"
        entity.description = None
        entity.width = 512
        entity.height = 768
        entity.repositoryType = "S3"
        entity.uri = "s3://bucket/image.jpg"
        entity.isAiGenerated = False
        entity.vectorId = None
        entity.uploadedAt = now
        entity.updatedAt = now

        # Assert
        assert entity.id == 1
        assert entity.ownerId == "owner-uuid-123"
        assert entity.title == "Test Image"
        assert entity.subtitle == "Test Subtitle"
        assert entity.description is None
        assert entity.width == 512
        assert entity.height == 768
        assert entity.repositoryType == "S3"
        assert entity.uri == "s3://bucket/image.jpg"
        assert entity.isAiGenerated is False
        assert entity.vectorId is None
        assert entity.uploadedAt == now
        assert entity.updatedAt == now

    def test_InitializeWithAllFields_ShouldSetCorrectValues(self):
        """Test that ImageMetadataEntity initializes with all fields."""
        # Arrange
        now = datetime.now(timezone.utc)

        # Act
        entity = ImageMetadataEntity()
        entity.id = 2
        entity.ownerId = "owner-uuid-456"
        entity.title = "Complete Image"
        entity.subtitle = "Complete Subtitle"
        entity.description = "A detailed description"
        entity.width = 1024
        entity.height = 1024
        entity.repositoryType = "MINIO"
        entity.uri = "minio://bucket/complete.png"
        entity.isAiGenerated = True
        entity.vectorId = 999
        entity.uploadedAt = now
        entity.updatedAt = now

        # Assert
        assert entity.id == 2
        assert entity.ownerId == "owner-uuid-456"
        assert entity.title == "Complete Image"
        assert entity.subtitle == "Complete Subtitle"
        assert entity.description == "A detailed description"
        assert entity.width == 1024
        assert entity.height == 1024
        assert entity.repositoryType == "MINIO"
        assert entity.uri == "minio://bucket/complete.png"
        assert entity.isAiGenerated is True
        assert entity.vectorId == 999
        assert entity.uploadedAt == now
        assert entity.updatedAt == now

    def test_ToDictWithMinimalData_ShouldReturnCorrectDictionary(self):
        """Test that ToDict returns correct dictionary with minimal data."""
        # Arrange
        now = datetime.now(timezone.utc)
        entity = ImageMetadataEntity()
        entity.id = 3
        entity.ownerId = "owner-uuid-789"
        entity.title = "Minimal Image"
        entity.subtitle = "Minimal Subtitle"
        entity.description = None
        entity.width = 256
        entity.height = 256
        entity.repositoryType = "LOCAL"
        entity.uri = "local://images/minimal.jpg"
        entity.isAiGenerated = False
        entity.vectorId = None
        entity.uploadedAt = now
        entity.updatedAt = now
        entity.generationMetadata = None

        # Act
        result = entity.ToDict()

        # Assert
        assert result["id"] == 3
        assert result["ownerId"] == "owner-uuid-789"
        assert result["title"] == "Minimal Image"
        assert result["subtitle"] == "Minimal Subtitle"
        assert result["description"] is None
        assert result["size"] == {"width": 256, "height": 256}
        assert result["repositoryType"] == "LOCAL"
        assert result["uri"] == "local://images/minimal.jpg"
        assert result["isAiGenerated"] is False
        assert result["generationMetadata"] is None
        assert result["vectorId"] is None
        assert result["uploadedAt"] == now
        assert result["updatedAt"] == now

    def test_ToDictWithGenerationMetadata_ShouldReturnGenerationMetadataDict(self):
        """Test that ToDict includes generation metadata when present."""
        # Arrange
        now = datetime.now(timezone.utc)
        entity = ImageMetadataEntity()
        entity.id = 4
        entity.ownerId = "owner-uuid-999"
        entity.title = "AI Generated Image"
        entity.subtitle = "AI Subtitle"
        entity.description = "Generated with AI"
        entity.width = 768
        entity.height = 512
        entity.repositoryType = "S3"
        entity.uri = "s3://bucket/ai.jpg"
        entity.isAiGenerated = True
        entity.vectorId = 555
        entity.uploadedAt = now
        entity.updatedAt = now

        # Mock generation metadata
        mockGenMetadata = MagicMock()
        mockGenMetadata.ToDict.return_value = {
            "id": 100,
            "imageId": 4,
            "prompt": "Test prompt",
            "negativePrompt": None,
            "seed": "12345",
            "model": "test_model",
            "sampler": SamplerType.EULER_A,
            "scheduler": SchedulerType.KARRAS,
            "steps": 20,
            "cfgScale": 7.0,
            "size": "768x512",
            "loras": [],
            "techniques": None,
        }
        entity.generationMetadata = mockGenMetadata

        # Act
        result = entity.ToDict()

        # Assert
        assert result["id"] == 4
        assert result["ownerId"] == "owner-uuid-999"
        assert result["title"] == "AI Generated Image"
        assert result["subtitle"] == "AI Subtitle"
        assert result["description"] == "Generated with AI"
        assert result["size"] == {"width": 768, "height": 512}
        assert result["repositoryType"] == "S3"
        assert result["uri"] == "s3://bucket/ai.jpg"
        assert result["isAiGenerated"] is True
        assert result["vectorId"] == 555
        assert result["generationMetadata"] is not None
        assert result["generationMetadata"]["id"] == 100
        assert result["generationMetadata"]["prompt"] == "Test prompt"
        assert result["uploadedAt"] == now
        assert result["updatedAt"] == now

    def test_ToDictWithNoneGenerationMetadata_ShouldReturnNone(self):
        """Test that ToDict returns None for generation metadata when not present."""
        # Arrange
        now = datetime.now(timezone.utc)
        entity = ImageMetadataEntity()
        entity.id = 5
        entity.ownerId = "owner-uuid-000"
        entity.title = "Non-AI Image"
        entity.subtitle = "Regular Photo"
        entity.description = None
        entity.width = 400
        entity.height = 300
        entity.repositoryType = "LOCAL"
        entity.uri = "local://images/photo.jpg"
        entity.isAiGenerated = False
        entity.vectorId = None
        entity.uploadedAt = now
        entity.updatedAt = now
        entity.generationMetadata = None

        # Act
        result = entity.ToDict()

        # Assert
        assert result["generationMetadata"] is None
