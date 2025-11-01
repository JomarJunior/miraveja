import pytest

from MiravejaApi.Gallery.Domain.Exceptions import (
    ImageMetadataNotFoundException,
    ImageMetadataAlreadyExistsException,
    ImageMetadataUriAlreadyExistsException,
    MalformedImageSizeStringException,
)
from MiravejaApi.Shared.Identifiers.Models import ImageMetadataId


class TestImageMetadataNotFoundException:
    """Test cases for ImageMetadataNotFoundException domain exception."""

    def test_InitializeWithImageMetadataId_ShouldSetCorrectMessage(self):
        """Test that ImageMetadataNotFoundException initializes with correct error message."""
        # Arrange
        image_id = ImageMetadataId(id=123)
        expected_message = f"Image metadata with ID '{image_id}' was not found."
        expected_code = 404

        # Act
        exception = ImageMetadataNotFoundException(image_id)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code

    def test_InitializeWithDifferentImageMetadataId_ShouldSetCorrectMessage(self):
        """Test that ImageMetadataNotFoundException handles different image metadata IDs."""
        # Arrange
        image_id = ImageMetadataId(id=999)
        expected_message = f"Image metadata with ID '{image_id}' was not found."
        expected_code = 404

        # Act
        exception = ImageMetadataNotFoundException(image_id)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code


class TestImageMetadataAlreadyExistsException:
    """Test cases for ImageMetadataAlreadyExistsException domain exception."""

    def test_InitializeWithImageMetadataId_ShouldSetCorrectMessage(self):
        """Test that ImageMetadataAlreadyExistsException initializes with correct error message."""
        # Arrange
        image_id = ImageMetadataId(id=456)
        expected_message = f"Image metadata with ID '{image_id}' already exists."
        expected_code = 409

        # Act
        exception = ImageMetadataAlreadyExistsException(image_id)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code


class TestImageMetadataUriAlreadyExistsException:
    """Test cases for ImageMetadataUriAlreadyExistsException domain exception."""

    def test_InitializeWithUri_ShouldSetCorrectMessage(self):
        """Test that ImageMetadataUriAlreadyExistsException initializes with correct error message."""
        # Arrange
        test_uri = "https://example.com/image.jpg"
        expected_message = f"Image metadata with URI '{test_uri}' already exists."
        expected_code = 409

        # Act
        exception = ImageMetadataUriAlreadyExistsException(test_uri)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code

    def test_InitializeWithEmptyUri_ShouldSetCorrectMessage(self):
        """Test that ImageMetadataUriAlreadyExistsException handles empty URI."""
        # Arrange
        test_uri = ""
        expected_message = f"Image metadata with URI '{test_uri}' already exists."
        expected_code = 409

        # Act
        exception = ImageMetadataUriAlreadyExistsException(test_uri)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code


class TestMalformedImageSizeStringException:
    """Test cases for MalformedImageSizeStringException domain exception."""

    def test_InitializeWithInvalidSizeString_ShouldSetCorrectMessage(self):
        """Test that MalformedImageSizeStringException initializes with correct error message."""
        # Arrange
        invalid_size = "invalid_size"
        expected_message = (
            f"Malformed size string: '{invalid_size}'. Expected format 'WIDTHxHEIGHT' with positive integers."
        )
        expected_code = 400

        # Act
        exception = MalformedImageSizeStringException(invalid_size)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code

    def test_InitializeWithEmptyString_ShouldSetCorrectMessage(self):
        """Test that MalformedImageSizeStringException handles empty string."""
        # Arrange
        invalid_size = ""
        expected_message = (
            f"Malformed size string: '{invalid_size}'. Expected format 'WIDTHxHEIGHT' with positive integers."
        )
        expected_code = 400

        # Act
        exception = MalformedImageSizeStringException(invalid_size)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code

    def test_InitializeWithAlmostValidSizeString_ShouldSetCorrectMessage(self):
        """Test that MalformedImageSizeStringException handles almost valid size string."""
        # Arrange
        invalid_size = "1920x"
        expected_message = (
            f"Malformed size string: '{invalid_size}'. Expected format 'WIDTHxHEIGHT' with positive integers."
        )
        expected_code = 400

        # Act
        exception = MalformedImageSizeStringException(invalid_size)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code
