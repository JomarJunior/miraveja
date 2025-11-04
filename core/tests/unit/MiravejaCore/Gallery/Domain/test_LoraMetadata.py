import pytest
from pydantic import ValidationError

from MiravejaCore.Gallery.Domain.Models import LoraMetadata
from MiravejaCore.Shared.Identifiers.Models import LoraMetadataId, GenerationMetadataId


class TestLoraMetadata:
    """Test cases for LoraMetadata domain model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that LoraMetadata initializes with valid data."""
        lora_id = LoraMetadataId(id=1)
        hash_value = "abc123def456"
        name = "TestLoRA"
        generation_ids = [GenerationMetadataId(id=1)]

        lora = LoraMetadata(id=lora_id, hash=hash_value, name=name, generationMetadatas=generation_ids)

        assert lora.id == lora_id
        assert lora.hash == hash_value
        assert lora.name == name
        assert lora.generationMetadatas == generation_ids

    def test_InitializeWithMinimalData_ShouldSetCorrectValues(self):
        """Test that LoraMetadata initializes with minimal required data."""
        lora_id = LoraMetadataId(id=1)
        hash_value = "abc123def456"

        lora = LoraMetadata(id=lora_id, hash=hash_value, name=None, generationMetadatas=None)

        assert lora.id == lora_id
        assert lora.hash == hash_value
        assert lora.name is None
        assert lora.generationMetadatas is None

    def test_InitializeWithEmptyHash_ShouldRaiseValidationError(self):
        """Test that LoraMetadata raises validation error with empty hash."""
        lora_id = LoraMetadataId(id=1)

        with pytest.raises(ValidationError) as exc_info:
            LoraMetadata(id=lora_id, hash="", name=None, generationMetadatas=None)

        assert "at least 1 character" in str(exc_info.value)

    def test_SerializeModel_ShouldReturnCorrectDict(self):
        """Test that SerializeModel returns correct dictionary structure."""
        lora_id = LoraMetadataId(id=1)
        hash_value = "abc123def456"
        name = "TestLoRA"

        lora = LoraMetadata(id=lora_id, hash=hash_value, name=name, generationMetadatas=None)

        result = lora.SerializeModel()

        assert result["id"] == int(lora_id)
        assert result["hash"] == hash_value
        assert result["name"] == name
        assert "generationMetadatas" not in result

    def test_SerializeModelWithNullName_ShouldReturnCorrectDict(self):
        """Test that SerializeModel handles null name correctly."""
        lora_id = LoraMetadataId(id=1)
        hash_value = "abc123def456"

        lora = LoraMetadata(id=lora_id, hash=hash_value, name=None, generationMetadatas=None)

        result = lora.SerializeModel()

        assert result["id"] == int(lora_id)
        assert result["hash"] == hash_value
        assert result["name"] is None

    def test_RegisterWithValidData_ShouldCreateCorrectInstance(self):
        """Test that Register factory method creates instance with valid data."""
        lora_id = LoraMetadataId(id=1)
        hash_value = "abc123def456"
        name = "TestLoRA"

        lora = LoraMetadata.Register(id=lora_id, hash=hash_value, name=name)

        assert lora.id == lora_id
        assert lora.hash == hash_value
        assert lora.name == name
        assert lora.generationMetadatas == []

    def test_RegisterWithoutName_ShouldCreateCorrectInstance(self):
        """Test that Register factory method creates instance without name."""
        lora_id = LoraMetadataId(id=1)
        hash_value = "abc123def456"

        lora = LoraMetadata.Register(id=lora_id, hash=hash_value)

        assert lora.id == lora_id
        assert lora.hash == hash_value
        assert lora.name is None
        assert lora.generationMetadatas == []

    def test_RegisterWithEmptyHash_ShouldRaiseValidationError(self):
        """Test that Register raises validation error with empty hash."""
        lora_id = LoraMetadataId(id=1)

        with pytest.raises(ValidationError) as exc_info:
            LoraMetadata.Register(id=lora_id, hash="")

        assert "at least 1 character" in str(exc_info.value)
