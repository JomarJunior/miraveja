import os
import io
import mimetypes
from typing import BinaryIO
from pydantic import BaseModel, Field

from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Storage.Domain.Enums import MimeType
from MiravejaCore.Shared.Utils.Constants.Binary import SIZE_1_MB


class ImageContent(BaseModel):
    binary: BinaryIO = Field(..., description="Binary stream of the image content")
    mimeType: MimeType = Field(..., description="MIME type of the image content")
    filename: str = Field("unnamed", description="Original filename of the image")
    ownerId: MemberId = Field(..., description="ID of the member who owns the image")

    model_config = {"arbitrary_types_allowed": True}

    @property
    def sizeBytes(self) -> int:
        """Get the size of the binary content in bytes."""
        currentPosition = self.binary.tell()
        self.binary.seek(0, io.SEEK_END)  # Move to end of file
        sizeBytes = self.binary.tell()
        self.binary.seek(currentPosition)  # Restore original position
        return sizeBytes

    @property
    def sizeMegabytes(self) -> float:
        """Get the size of the binary content in megabytes."""
        return self.sizeBytes / SIZE_1_MB

    @property
    def extension(self) -> str:
        """Get the file extension based on the MIME type."""
        extension = mimetypes.guess_extension(self.mimeType)
        if extension is None:
            # Fallback to using the filename extension if MIME type is unknown
            extension = os.path.splitext(self.filename)[1]
        return extension if extension else ""
