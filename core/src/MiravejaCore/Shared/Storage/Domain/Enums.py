from enum import Enum


class Region(str, Enum):
    """Enumeration of supported regions."""

    US_EAST_1 = "us-east-1"
    US_WEST_1 = "us-west-1"
    US_WEST_2 = "us-west-2"
    EU_WEST_1 = "eu-west-1"
    EU_CENTRAL_1 = "eu-central-1"
    SA_EAST_1 = "sa-east-1"

    def __str__(self) -> str:
        return self.value


class MimeType(str, Enum):
    """Enumeration of supported MIME types."""

    JPEG = "image/jpeg"
    PNG = "image/png"
    GIF = "image/gif"
    BMP = "image/bmp"
    TIFF = "image/tiff"
    WEBP = "image/webp"
    PDF = "application/pdf"
    ZIP = "application/zip"
    JSON = "application/json"
    XML = "application/xml"
    HTML = "text/html"
    PLAIN = "text/plain"

    def __str__(self) -> str:
        return self.value

    def ToExtension(self) -> str:
        """Convert MIME type to file extension."""
        mapping = {
            MimeType.JPEG: "jpeg",
            MimeType.PNG: "png",
            MimeType.GIF: "gif",
            MimeType.BMP: "bmp",
            MimeType.TIFF: "tiff",
            MimeType.WEBP: "webp",
            MimeType.PDF: "pdf",
            MimeType.ZIP: "zip",
            MimeType.JSON: "json",
            MimeType.XML: "xml",
            MimeType.HTML: "html",
            MimeType.PLAIN: "txt",
        }
        return mapping.get(self, "bin")
