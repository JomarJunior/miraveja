import io
from typing import BinaryIO

from PIL import Image

from MiravejaCore.Gallery.Application.GetPresignedPostUrl import MimeType
from MiravejaCore.Gallery.Domain.Interfaces import IThumbnailGenerationService
from MiravejaCore.Gallery.Domain.Models import Size


class PillowThumbnailGenerationService(IThumbnailGenerationService):
    def __init__(self, size: Size, imgFormat: MimeType):
        self._size = size
        if imgFormat not in {MimeType.PNG, MimeType.JPEG}:
            raise ValueError("Unsupported image format for thumbnail generation.")
        self.format = imgFormat

    async def GenerateThumbnail(self, image: BinaryIO) -> BinaryIO:
        pilImage = Image.open(image)
        pilImage.load()  # ensure full decode

        pilImage.thumbnail((self._size.width, self._size.height))

        if self.format == MimeType.JPEG and pilImage.mode not in ("RGB", "L"):
            pilImage = pilImage.convert("RGB")  # Ensure no alpha channel for JPEG

        output = io.BytesIO()
        pilImage.save(output, format=self.format.ToExtension())

        output.seek(0)  # pylint: disable=E1101
        return output
