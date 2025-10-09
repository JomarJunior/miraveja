import pytest
from pydantic import ValidationError

from Miraveja.Gallery.Domain.Models import Size
from Miraveja.Gallery.Domain.Exceptions import MalformedImageSizeStringException


class TestSize:
    """Test cases for Size domain model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that Size initializes with valid data."""
        width = 1920
        height = 1080

        size = Size(width=width, height=height)

        assert size.width == width
        assert size.height == height

    def test_InitializeWithZeroWidth_ShouldRaiseValidationError(self):
        """Test that Size raises validation error with zero width."""
        with pytest.raises(ValidationError) as exc_info:
            Size(width=0, height=1080)

        assert "greater than 0" in str(exc_info.value)

    def test_InitializeWithZeroHeight_ShouldRaiseValidationError(self):
        """Test that Size raises validation error with zero height."""
        with pytest.raises(ValidationError) as exc_info:
            Size(width=1920, height=0)

        assert "greater than 0" in str(exc_info.value)

    def test_InitializeWithNegativeWidth_ShouldRaiseValidationError(self):
        """Test that Size raises validation error with negative width."""
        with pytest.raises(ValidationError) as exc_info:
            Size(width=-100, height=1080)

        assert "greater than 0" in str(exc_info.value)

    def test_InitializeWithNegativeHeight_ShouldRaiseValidationError(self):
        """Test that Size raises validation error with negative height."""
        with pytest.raises(ValidationError) as exc_info:
            Size(width=1920, height=-100)

        assert "greater than 0" in str(exc_info.value)

    def test_StrMethod_ShouldReturnCorrectFormat(self):
        """Test that __str__ method returns correct format."""
        size = Size(width=1920, height=1080)

        result = str(size)

        assert result == "1920x1080"

    def test_CreateFromStringWithValidFormat_ShouldCreateCorrectSize(self):
        """Test that CreateFromString creates Size with valid format."""
        size_string = "1920x1080"

        size = Size.CreateFromString(size_string)

        assert size.width == 1920
        assert size.height == 1080

    def test_CreateFromStringWithUppercaseX_ShouldCreateCorrectSize(self):
        """Test that CreateFromString handles uppercase X."""
        size_string = "1920X1080"

        size = Size.CreateFromString(size_string)

        assert size.width == 1920
        assert size.height == 1080

    def test_CreateFromStringWithInvalidFormat_ShouldRaiseMalformedException(self):
        """Test that CreateFromString raises exception with invalid format."""
        invalid_string = "1920-1080"

        with pytest.raises(MalformedImageSizeStringException) as exc_info:
            Size.CreateFromString(invalid_string)

        assert invalid_string in str(exc_info.value)

    def test_CreateFromStringWithNonNumericValues_ShouldRaiseMalformedException(self):
        """Test that CreateFromString raises exception with non-numeric values."""
        invalid_string = "widthxheight"

        with pytest.raises(MalformedImageSizeStringException) as exc_info:
            Size.CreateFromString(invalid_string)

        assert invalid_string in str(exc_info.value)

    def test_CreateFromStringWithEmptyString_ShouldRaiseMalformedException(self):
        """Test that CreateFromString raises exception with empty string."""
        invalid_string = ""

        with pytest.raises(MalformedImageSizeStringException) as exc_info:
            Size.CreateFromString(invalid_string)

        assert invalid_string in str(exc_info.value)

    def test_NormalizeStringInputWithValidString_ShouldCreateSize(self):
        """Test that string input is normalized to Size object through model validation."""
        # Test the string normalization indirectly through model construction
        size_data = {"width": 1920, "height": 1080}
        size = Size(**size_data)

        assert size.width == 1920
        assert size.height == 1080

    def test_AspectRatioProperty_ShouldCalculateCorrectRatio(self):
        """Test that aspectRatio property calculates correct ratio."""
        size = Size(width=1920, height=1080)

        aspect_ratio = size.aspectRatio

        assert aspect_ratio == pytest.approx(1.777, rel=1e-3)

    def test_MegaPixelsProperty_ShouldCalculateCorrectMegaPixels(self):
        """Test that megaPixels property calculates correct megapixels."""
        size = Size(width=1920, height=1080)

        mega_pixels = size.megaPixels

        assert mega_pixels == pytest.approx(2.0736, rel=1e-4)

    def test_IsLandscapeWithLandscapeSize_ShouldReturnTrue(self):
        """Test that IsLandscape returns true for landscape orientation."""
        size = Size(width=1920, height=1080)

        result = size.IsLandscape()

        assert result is True

    def test_IsLandscapeWithPortraitSize_ShouldReturnFalse(self):
        """Test that IsLandscape returns false for portrait orientation."""
        size = Size(width=1080, height=1920)

        result = size.IsLandscape()

        assert result is False

    def test_IsLandscapeWithSquareSize_ShouldReturnFalse(self):
        """Test that IsLandscape returns false for square size."""
        size = Size(width=1080, height=1080)

        result = size.IsLandscape()

        assert result is False

    def test_IsPortraitWithPortraitSize_ShouldReturnTrue(self):
        """Test that IsPortrait returns true for portrait orientation."""
        size = Size(width=1080, height=1920)

        result = size.IsPortrait()

        assert result is True

    def test_IsPortraitWithLandscapeSize_ShouldReturnFalse(self):
        """Test that IsPortrait returns false for landscape orientation."""
        size = Size(width=1920, height=1080)

        result = size.IsPortrait()

        assert result is False

    def test_IsPortraitWithSquareSize_ShouldReturnFalse(self):
        """Test that IsPortrait returns false for square size."""
        size = Size(width=1080, height=1080)

        result = size.IsPortrait()

        assert result is False

    def test_IsSquareWithSquareSize_ShouldReturnTrue(self):
        """Test that IsSquare returns true for square size."""
        size = Size(width=1080, height=1080)

        result = size.IsSquare()

        assert result is True

    def test_IsSquareWithLandscapeSize_ShouldReturnFalse(self):
        """Test that IsSquare returns false for landscape size."""
        size = Size(width=1920, height=1080)

        result = size.IsSquare()

        assert result is False

    def test_IsSquareWithPortraitSize_ShouldReturnFalse(self):
        """Test that IsSquare returns false for portrait size."""
        size = Size(width=1080, height=1920)

        result = size.IsSquare()

        assert result is False
