"""
Unit tests for Acquisition Domain Models.
"""

import pytest
import json
from unittest.mock import Mock
from pydantic import ValidationError

from src.Acquisition.Domain.Models import Provider, Image, ImageContent

class TestProvider:
    """Test cases for the Provider model."""

    def test_provider_creation_with_valid_data(self):
        """Test creating a Provider with valid data."""
        provider = Provider(id=1, name="TestProvider")
        
        assert provider.id == 1
        assert provider.name == "TestProvider"

    def test_provider_creation_with_all_fields(self):
        """Test creating a Provider with all required fields."""
        provider_data = {
            "id": 123,
            "name": "Sample Provider"
        }
        provider = Provider(**provider_data)
        
        assert provider.id == 123
        assert provider.name == "Sample Provider"

    def test_provider_missing_id_raises_error(self):
        """Test that missing id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Provider(name="TestProvider") # type: ignore
        
        assert "id" in str(exc_info.value)

    def test_provider_missing_name_raises_error(self):
        """Test that missing name raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Provider(id=1) # type: ignore
        
        assert "name" in str(exc_info.value)

    def test_provider_invalid_id_type_raises_error(self):
        """Test that invalid id type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Provider(id="invalid", name="TestProvider") # type: ignore
        
        assert "id" in str(exc_info.value)

    def test_provider_invalid_name_type_raises_error(self):
        """Test that invalid name type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Provider(id=1, name=123) # type: ignore
        
        assert "name" in str(exc_info.value)

    def test_provider_to_dict(self):
        """Test Provider to_dict method."""
        provider = Provider(id=1, name="TestProvider")
        result = provider.to_dict()
        
        expected = {
            "id": 1,
            "name": "TestProvider"
        }
        assert result == expected

    def test_provider_from_dict_with_valid_data(self):
        """Test Provider.from_dict with valid data."""
        data = {
            "id": 42,
            "name": "Valid Provider"
        }
        provider = Provider.from_dict(data)
        
        assert provider.id == 42
        assert provider.name == "Valid Provider"

    def test_provider_from_dict_missing_id(self):
        """Test Provider.from_dict raises error when id is missing."""
        data = {"name": "TestProvider"}
        
        with pytest.raises(ValueError) as exc_info:
            Provider.from_dict(data)
        
        assert "Missing 'id' field" in str(exc_info.value)

    def test_provider_from_dict_missing_name(self):
        """Test Provider.from_dict raises error when name is missing."""
        data = {"id": 1}
        
        with pytest.raises(ValueError) as exc_info:
            Provider.from_dict(data)
        
        assert "Missing 'name' field" in str(exc_info.value)

    def test_provider_from_dict_empty_id(self):
        """Test Provider.from_dict raises error when id is empty/None."""
        data = {"id": None, "name": "TestProvider"}
        
        with pytest.raises(ValueError) as exc_info:
            Provider.from_dict(data)
        
        assert "Missing 'id' field" in str(exc_info.value)

    def test_provider_from_dict_empty_name(self):
        """Test Provider.from_dict raises error when name is empty."""
        data = {"id": 1, "name": ""}
        
        with pytest.raises(ValueError) as exc_info:
            Provider.from_dict(data)
        
        assert "Missing 'name' field" in str(exc_info.value)

    def test_provider_round_trip_serialization(self):
        """Test Provider serialization and deserialization round trip."""
        original = Provider(id=100, name="Round Trip Provider")
        data = original.to_dict()
        restored = Provider.from_dict(data)
        
        assert original.id == restored.id
        assert original.name == restored.name


class TestImage:
    """Test cases for the Image model."""

    @pytest.fixture
    def sample_provider(self):
        """Fixture providing a sample provider."""
        return Provider(id=1, name="Sample Provider")

    @pytest.fixture
    def sample_metadata(self):
        """Fixture providing sample metadata."""
        return {
            "width": 1920,
            "height": 1080,
            "format": "JPEG",
            "size_bytes": 2048000
        }

    def test_image_creation_with_valid_data(self, sample_provider, sample_metadata):
        """Test creating an Image with valid data."""
        image = Image(
            id=1,
            uri="https://example.com/image.jpg",
            metadata=sample_metadata,
            provider_id=1,
            provider=sample_provider
        )
        
        assert image.id == 1
        assert image.uri == "https://example.com/image.jpg"
        assert image.metadata == sample_metadata
        assert image.provider_id == 1
        assert image.provider == sample_provider

    def test_image_creation_with_all_fields(self, sample_provider, sample_metadata):
        """Test creating an Image with all required fields."""
        image_data = {
            "id": 123,
            "uri": "https://test.com/test.png",
            "metadata": sample_metadata,
            "provider_id": 456,
            "provider": sample_provider
        }
        image = Image(**image_data)
        
        assert image.id == 123
        assert image.uri == "https://test.com/test.png"
        assert image.metadata == sample_metadata
        assert image.provider_id == 456
        assert image.provider == sample_provider

    def test_image_missing_id_raises_error(self, sample_provider, sample_metadata):
        """Test that missing id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Image(
                uri="https://example.com/image.jpg",
                metadata=sample_metadata,
                provider_id=1,
                provider=sample_provider
            ) # type: ignore
        
        assert "id" in str(exc_info.value)

    def test_image_missing_uri_raises_error(self, sample_provider, sample_metadata):
        """Test that missing uri raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Image(
                id=1,
                metadata=sample_metadata,
                provider_id=1,
                provider=sample_provider
            ) # type: ignore
        
        assert "uri" in str(exc_info.value)

    def test_image_missing_metadata_raises_error(self, sample_provider):
        """Test that missing metadata raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Image(
                id=1,
                uri="https://example.com/image.jpg",
                provider_id=1,
                provider=sample_provider
            ) # type: ignore
        
        assert "metadata" in str(exc_info.value)

    def test_image_missing_provider_id_raises_error(self, sample_provider, sample_metadata):
        """Test that missing provider_id raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Image(
                id=1,
                uri="https://example.com/image.jpg",
                metadata=sample_metadata,
                provider=sample_provider
            ) # type: ignore
        
        assert "provider_id" in str(exc_info.value)

    def test_image_missing_provider_raises_error(self, sample_metadata):
        """Test that missing provider raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Image(
                id=1,
                uri="https://example.com/image.jpg",
                metadata=sample_metadata,
                provider_id=1
            ) # type: ignore
        
        assert "provider" in str(exc_info.value)

    def test_image_invalid_types_raise_errors(self, sample_provider):
        """Test that invalid field types raise ValidationError."""
        # Invalid id type
        with pytest.raises(ValidationError):
            Image(
                id="invalid", # type: ignore
                uri="https://example.com/image.jpg",
                metadata={},
                provider_id=1,
                provider=sample_provider
            )
        
        # Invalid uri type
        with pytest.raises(ValidationError):
            Image(
                id=1,
                uri=123, # type: ignore
                metadata={},
                provider_id=1,
                provider=sample_provider
            )
        
        # Invalid metadata type
        with pytest.raises(ValidationError):
            Image(
                id=1,
                uri="https://example.com/image.jpg",
                metadata="invalid", # type: ignore
                provider_id=1,
                provider=sample_provider
            )

    def test_image_to_dict(self, sample_provider, sample_metadata):
        """Test Image to_dict method."""
        image = Image(
            id=1,
            uri="https://example.com/image.jpg",
            metadata=sample_metadata,
            provider_id=1,
            provider=sample_provider
        )
        result = image.to_dict()
        
        expected = {
            "id": 1,
            "uri": "https://example.com/image.jpg",
            "metadata": sample_metadata,
            "provider_id": 1,
            "provider": {
                "id": 1,
                "name": "Sample Provider"
            }
        }
        assert result == expected

    def test_image_from_dict_with_valid_data(self, sample_metadata):
        """Test Image.from_dict with valid data."""
        data = {
            "id": 42,
            "uri": "https://valid.com/image.jpg",
            "metadata": sample_metadata,
            "provider_id": 10,
            "provider": {
                "id": 10,
                "name": "Valid Provider"
            }
        }
        image = Image.from_dict(data)
        
        assert image.id == 42
        assert image.uri == "https://valid.com/image.jpg"
        assert image.metadata == sample_metadata
        assert image.provider_id == 10
        assert image.provider.id == 10
        assert image.provider.name == "Valid Provider"

    def test_image_from_dict_missing_fields(self):
        """Test Image.from_dict raises errors for missing fields."""
        base_data = {
            "id": 1,
            "uri": "https://example.com/image.jpg",
            "metadata": {"test": "data"},
            "provider_id": 1,
            "provider": {"id": 1, "name": "Test Provider"}
        }
        
        # Test missing id
        data = base_data.copy()
        del data["id"]
        with pytest.raises(ValueError) as exc_info:
            Image.from_dict(data)
        assert "Missing 'id' field" in str(exc_info.value)
        
        # Test missing uri
        data = base_data.copy()
        del data["uri"]
        with pytest.raises(ValueError) as exc_info:
            Image.from_dict(data)
        assert "Missing 'uri' field" in str(exc_info.value)
        
        # Test missing metadata
        data = base_data.copy()
        del data["metadata"]
        with pytest.raises(ValueError) as exc_info:
            Image.from_dict(data)
        assert "Missing 'metadata' field" in str(exc_info.value)
        
        # Test missing provider_id
        data = base_data.copy()
        del data["provider_id"]
        with pytest.raises(ValueError) as exc_info:
            Image.from_dict(data)
        assert "Missing 'provider_id' field" in str(exc_info.value)
        
        # Test missing provider
        data = base_data.copy()
        del data["provider"]
        with pytest.raises(ValueError) as exc_info:
            Image.from_dict(data)
        assert "Missing 'provider' field" in str(exc_info.value)

    def test_image_from_dict_empty_fields(self):
        """Test Image.from_dict raises errors for empty/None fields."""
        base_data = {
            "id": 1,
            "uri": "https://example.com/image.jpg",
            "metadata": {"test": "data"},
            "provider_id": 1,
            "provider": {"id": 1, "name": "Test Provider"}
        }
        
        # Test empty id
        data = base_data.copy()
        data["id"] = None
        with pytest.raises(ValueError) as exc_info:
            Image.from_dict(data)
        assert "Missing 'id' field" in str(exc_info.value)
        
        # Test empty uri
        data = base_data.copy()
        data["uri"] = ""
        with pytest.raises(ValueError) as exc_info:
            Image.from_dict(data)
        assert "Missing 'uri' field" in str(exc_info.value)

    def test_image_round_trip_serialization(self, sample_provider, sample_metadata):
        """Test Image serialization and deserialization round trip."""
        original = Image(
            id=100,
            uri="https://roundtrip.com/image.jpg",
            metadata=sample_metadata,
            provider_id=200,
            provider=sample_provider
        )
        data = original.to_dict()
        restored = Image.from_dict(data)
        
        assert original.id == restored.id
        assert original.uri == restored.uri
        assert original.metadata == restored.metadata
        assert original.provider_id == restored.provider_id
        assert original.provider.id == restored.provider.id
        assert original.provider.name == restored.provider.name


class TestImageContent:
    """Test cases for the ImageContent model."""

    @pytest.fixture
    def sample_base64_content(self):
        """Fixture providing sample base64 content."""
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    def test_image_content_creation_with_valid_data(self, sample_base64_content):
        """Test creating ImageContent with valid data."""
        image_content = ImageContent(
            uri="https://example.com/image.jpg",
            base64_content=sample_base64_content
        )
        
        assert image_content.uri == "https://example.com/image.jpg"
        assert image_content.base64_content == sample_base64_content

    def test_image_content_creation_with_all_fields(self, sample_base64_content):
        """Test creating ImageContent with all required fields."""
        content_data = {
            "uri": "https://test.com/test.png",
            "base64_content": sample_base64_content
        }
        image_content = ImageContent(**content_data)
        
        assert image_content.uri == "https://test.com/test.png"
        assert image_content.base64_content == sample_base64_content

    def test_image_content_missing_uri_raises_error(self, sample_base64_content):
        """Test that missing uri raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ImageContent(base64_content=sample_base64_content) # type: ignore
        
        assert "uri" in str(exc_info.value)

    def test_image_content_missing_base64_content_raises_error(self):
        """Test that missing base64_content raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ImageContent(uri="https://example.com/image.jpg") # type: ignore
        
        assert "base64_content" in str(exc_info.value)

    def test_image_content_invalid_types_raise_errors(self, sample_base64_content):
        """Test that invalid field types raise ValidationError."""
        # Invalid uri type
        with pytest.raises(ValidationError):
            ImageContent(
                uri=123, # type: ignore
                base64_content=sample_base64_content
            )
        
        # Invalid base64_content type
        with pytest.raises(ValidationError):
            ImageContent(
                uri="https://example.com/image.jpg",
                base64_content=123 # type: ignore
            )

    def test_image_content_to_dict(self, sample_base64_content):
        """Test ImageContent to_dict method."""
        image_content = ImageContent(
            uri="https://example.com/image.jpg",
            base64_content=sample_base64_content
        )
        result = image_content.to_dict()
        
        expected = {
            "uri": "https://example.com/image.jpg",
            "base64_content": sample_base64_content
        }
        assert result == expected

    def test_image_content_from_dict_with_valid_data(self, sample_base64_content):
        """Test ImageContent.from_dict with valid data."""
        data = {
            "uri": "https://valid.com/image.jpg",
            "base64_content": sample_base64_content
        }
        image_content = ImageContent.from_dict(data)
        
        assert image_content.uri == "https://valid.com/image.jpg"
        assert image_content.base64_content == sample_base64_content

    def test_image_content_from_dict_missing_uri(self, sample_base64_content):
        """Test ImageContent.from_dict raises error when uri is missing."""
        data = {"base64_content": sample_base64_content}
        
        with pytest.raises(ValueError) as exc_info:
            ImageContent.from_dict(data)
        
        assert "Missing 'uri' field" in str(exc_info.value)

    def test_image_content_from_dict_missing_base64_content(self):
        """Test ImageContent.from_dict raises error when base64_content is missing."""
        data = {"uri": "https://example.com/image.jpg"}
        
        with pytest.raises(ValueError) as exc_info:
            ImageContent.from_dict(data)
        
        assert "Missing 'base64_content' field" in str(exc_info.value)

    def test_image_content_from_dict_empty_uri(self, sample_base64_content):
        """Test ImageContent.from_dict raises error when uri is empty."""
        data = {"uri": "", "base64_content": sample_base64_content}
        
        with pytest.raises(ValueError) as exc_info:
            ImageContent.from_dict(data)
        
        assert "Missing 'uri' field" in str(exc_info.value)

    def test_image_content_from_dict_empty_base64_content(self):
        """Test ImageContent.from_dict raises error when base64_content is empty."""
        data = {"uri": "https://example.com/image.jpg", "base64_content": ""}
        
        with pytest.raises(ValueError) as exc_info:
            ImageContent.from_dict(data)
        
        assert "Missing 'base64_content' field" in str(exc_info.value)

    def test_image_content_from_dict_none_values(self):
        """Test ImageContent.from_dict raises error when values are None."""
        # Test None uri
        data = {"uri": None, "base64_content": "valid_content"}
        with pytest.raises(ValueError) as exc_info:
            ImageContent.from_dict(data)
        assert "Missing 'uri' field" in str(exc_info.value)
        
        # Test None base64_content
        data = {"uri": "https://example.com/image.jpg", "base64_content": None}
        with pytest.raises(ValueError) as exc_info:
            ImageContent.from_dict(data)
        assert "Missing 'base64_content' field" in str(exc_info.value)

    def test_image_content_round_trip_serialization(self, sample_base64_content):
        """Test ImageContent serialization and deserialization round trip."""
        original = ImageContent(
            uri="https://roundtrip.com/image.jpg",
            base64_content=sample_base64_content
        )
        data = original.to_dict()
        restored = ImageContent.from_dict(data)
        
        assert original.uri == restored.uri
        assert original.base64_content == restored.base64_content

    def test_image_content_with_different_uri_formats(self, sample_base64_content):
        """Test ImageContent with various URI formats."""
        uri_formats = [
            "https://example.com/image.jpg",
            "http://localhost:8080/image.png",
            "/local/path/image.gif",
            "file:///absolute/path/image.bmp",
            "s3://bucket/image.tiff"
        ]
        
        for uri in uri_formats:
            image_content = ImageContent(uri=uri, base64_content=sample_base64_content)
            assert image_content.uri == uri
            assert image_content.base64_content == sample_base64_content

    def test_image_content_with_large_base64_content(self):
        """Test ImageContent with larger base64 content."""
        # Create a larger base64 string (simulating a larger image)
        large_base64 = "a" * 10000  # 10KB of 'a' characters
        
        image_content = ImageContent(
            uri="https://example.com/large_image.jpg",
            base64_content=large_base64
        )
        
        assert image_content.uri == "https://example.com/large_image.jpg"
        assert image_content.base64_content == large_base64
        assert len(image_content.base64_content) == 10000


class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_provider_and_image_integration(self):
        """Test Provider and Image models working together."""
        # Create a provider
        provider = Provider(id=1, name="Integration Provider")
        
        # Create an image with the provider
        metadata = {"width": 800, "height": 600, "format": "PNG"}
        image = Image(
            id=100,
            uri="https://integration.com/image.png",
            metadata=metadata,
            provider_id=provider.id,
            provider=provider
        )
        
        # Test that the relationship works
        assert image.provider.id == provider.id
        assert image.provider.name == provider.name
        assert image.provider_id == provider.id

    def test_all_models_serialization_integration(self):
        """Test serialization/deserialization of all models together."""
        # Create provider
        provider_data = {"id": 1, "name": "Test Provider"}
        provider = Provider.from_dict(provider_data)
        
        # Create image
        image_data = {
            "id": 200,
            "uri": "https://test.com/test.jpg",
            "metadata": {"size": 1024, "type": "JPEG"},
            "provider_id": 1,
            "provider": provider_data
        }
        image = Image.from_dict(image_data)
        
        # Create image content
        content_data = {
            "uri": "https://test.com/test.jpg",
            "base64_content": "base64encodedcontent"
        }
        image_content = ImageContent.from_dict(content_data)
        
        # Test all models can serialize back
        provider_dict = provider.to_dict()
        image_dict = image.to_dict()
        content_dict = image_content.to_dict()
        
        # Verify serialization works
        assert provider_dict["id"] == 1
        assert image_dict["provider"]["name"] == "Test Provider"
        assert content_dict["uri"] == "https://test.com/test.jpg"
        
        # Test deserialization round trip
        restored_provider = Provider.from_dict(provider_dict)
        restored_image = Image.from_dict(image_dict)
        restored_content = ImageContent.from_dict(content_dict)
        
        assert restored_provider.id == provider.id
        assert restored_image.uri == image.uri
        assert restored_content.base64_content == image_content.base64_content
