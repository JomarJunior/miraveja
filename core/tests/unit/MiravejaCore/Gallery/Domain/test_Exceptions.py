import pytest

from MiravejaCore.Gallery.Domain.Exceptions import (
    ImageMetadataAlreadyExistsException,
    ImageMetadataNotFoundException,
    ImageMetadataUriAlreadyExistsException,
    MalformedImageSizeStringException,
)
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId


class TestMalformedImageSizeStringException:
    """Test cases for MalformedImageSizeStringException."""

    def test_InitializeWithInvalidSizeString_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message and details."""
        invalid_size_string = "invalid_size"

        exception = MalformedImageSizeStringException(invalid_size_string)

        expected_message = (
            f"Malformed size string: '{invalid_size_string}'. Expected format 'WIDTHxHEIGHT' with positive integers."
        )
        assert str(exception) == expected_message
        assert exception.code == 400
        assert exception.details is not None
        assert exception.details["sizeString"] == invalid_size_string

    def test_InitializeWithEmptyString_ShouldSetCorrectMessage(self):
        """Test that exception handles empty string correctly."""
        empty_string = ""

        exception = MalformedImageSizeStringException(empty_string)

        expected_message = (
            f"Malformed size string: '{empty_string}'. Expected format 'WIDTHxHEIGHT' with positive integers."
        )
        assert str(exception) == expected_message
        assert exception.code == 400
        assert exception.details is not None
        assert exception.details["sizeString"] == empty_string


class TestImageMetadataNotFoundException:
    """Test cases for ImageMetadataNotFoundException."""

    def test_InitializeWithImageId_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message and details."""
        image_id = ImageMetadataId(id=123)

        exception = ImageMetadataNotFoundException(image_id)

        expected_message = f"Image metadata with ID '{image_id}' was not found."
        assert str(exception) == expected_message
        assert exception.code == 404
        assert exception.details is not None
        assert exception.details["imageId"] == image_id


class TestImageMetadataAlreadyExistsException:
    """Test cases for ImageMetadataAlreadyExistsException."""

    def test_InitializeWithImageId_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message and details."""
        image_id = ImageMetadataId(id=456)

        exception = ImageMetadataAlreadyExistsException(image_id)

        expected_message = f"Image metadata with ID '{image_id}' already exists."
        assert str(exception) == expected_message
        assert exception.code == 409
        assert exception.details is not None
        assert exception.details["imageId"] == image_id


class TestImageMetadataUriAlreadyExistsException:
    """Test cases for ImageMetadataUriAlreadyExistsException."""

    def test_InitializeWithUri_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message and details."""
        uri = "https://example.com/duplicate-image.jpg"

        exception = ImageMetadataUriAlreadyExistsException(uri)

        expected_message = f"Image metadata with URI '{uri}' already exists."
        assert str(exception) == expected_message
        assert exception.code == 409
        assert exception.details is not None
        assert exception.details["uri"] == uri

    def test_InitializeWithEmptyUri_ShouldSetCorrectMessage(self):
        """Test that exception handles empty URI correctly."""
        empty_uri = ""

        exception = ImageMetadataUriAlreadyExistsException(empty_uri)

        expected_message = f"Image metadata with URI '{empty_uri}' already exists."
        assert str(exception) == expected_message
        assert exception.code == 409
        assert exception.details is not None
        assert exception.details["uri"] == empty_uri
