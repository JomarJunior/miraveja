import pytest

from MiravejaCore.Shared.Storage.Domain.Enums import Region, MimeType


class TestRegion:
    """Test cases for Region enum."""

    def test_UsEast1Value_ShouldReturnCorrectString(self):
        """Test that US_EAST_1 enum has correct value."""
        assert Region.US_EAST_1.value == "us-east-1"

    def test_UsWest1Value_ShouldReturnCorrectString(self):
        """Test that US_WEST_1 enum has correct value."""
        assert Region.US_WEST_1.value == "us-west-1"

    def test_UsWest2Value_ShouldReturnCorrectString(self):
        """Test that US_WEST_2 enum has correct value."""
        assert Region.US_WEST_2.value == "us-west-2"

    def test_EuWest1Value_ShouldReturnCorrectString(self):
        """Test that EU_WEST_1 enum has correct value."""
        assert Region.EU_WEST_1.value == "eu-west-1"

    def test_EuCentral1Value_ShouldReturnCorrectString(self):
        """Test that EU_CENTRAL_1 enum has correct value."""
        assert Region.EU_CENTRAL_1.value == "eu-central-1"

    def test_SaEast1Value_ShouldReturnCorrectString(self):
        """Test that SA_EAST_1 enum has correct value."""
        assert Region.SA_EAST_1.value == "sa-east-1"

    def test_StrMethod_ShouldReturnEnumValue(self):
        """Test that __str__ method returns the enum value."""
        assert str(Region.US_EAST_1) == "us-east-1"
        assert str(Region.US_WEST_1) == "us-west-1"
        assert str(Region.EU_CENTRAL_1) == "eu-central-1"


class TestMimeType:
    """Test cases for MimeType enum."""

    def test_JpegValue_ShouldReturnCorrectString(self):
        """Test that JPEG enum has correct value."""
        assert MimeType.JPEG.value == "image/jpeg"

    def test_PngValue_ShouldReturnCorrectString(self):
        """Test that PNG enum has correct value."""
        assert MimeType.PNG.value == "image/png"

    def test_GifValue_ShouldReturnCorrectString(self):
        """Test that GIF enum has correct value."""
        assert MimeType.GIF.value == "image/gif"

    def test_BmpValue_ShouldReturnCorrectString(self):
        """Test that BMP enum has correct value."""
        assert MimeType.BMP.value == "image/bmp"

    def test_TiffValue_ShouldReturnCorrectString(self):
        """Test that TIFF enum has correct value."""
        assert MimeType.TIFF.value == "image/tiff"

    def test_WebpValue_ShouldReturnCorrectString(self):
        """Test that WEBP enum has correct value."""
        assert MimeType.WEBP.value == "image/webp"

    def test_PdfValue_ShouldReturnCorrectString(self):
        """Test that PDF enum has correct value."""
        assert MimeType.PDF.value == "application/pdf"

    def test_ZipValue_ShouldReturnCorrectString(self):
        """Test that ZIP enum has correct value."""
        assert MimeType.ZIP.value == "application/zip"

    def test_JsonValue_ShouldReturnCorrectString(self):
        """Test that JSON enum has correct value."""
        assert MimeType.JSON.value == "application/json"

    def test_XmlValue_ShouldReturnCorrectString(self):
        """Test that XML enum has correct value."""
        assert MimeType.XML.value == "application/xml"

    def test_HtmlValue_ShouldReturnCorrectString(self):
        """Test that HTML enum has correct value."""
        assert MimeType.HTML.value == "text/html"

    def test_PlainValue_ShouldReturnCorrectString(self):
        """Test that PLAIN enum has correct value."""
        assert MimeType.PLAIN.value == "text/plain"

    def test_StrMethod_ShouldReturnEnumValue(self):
        """Test that __str__ method returns the enum value."""
        assert str(MimeType.JPEG) == "image/jpeg"
        assert str(MimeType.PNG) == "image/png"
        assert str(MimeType.JSON) == "application/json"
        assert str(MimeType.PLAIN) == "text/plain"
