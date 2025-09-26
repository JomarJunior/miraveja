"""
Implements the thumbnail generation service.
"""

import base64
from io import BytesIO
from src.Processing.Domain.Enums import ImageExtensionEnum
from src.Processing.Domain.Interfaces import IThumbnailService, IStorageService
from src.Processing.Domain.Models import ImageThumbnail
from PIL import Image

class PillowThumbnailService(IThumbnailService):
    """
    Implements the thumbnail generation service using Pillow.
    Pillow is a Python Imaging Library that adds image processing capabilities to your Python interpreter.
    """
    def __init__(
            self,
            dimensions: tuple[int, int],
            extension: ImageExtensionEnum,
            storage_service: IStorageService
    ):
        self.storage_service: IStorageService = storage_service
        self.dimensions: tuple[int, int] = dimensions
        self.extension: ImageExtensionEnum = extension


    def generate_image_thumbnail(self, image_id: int) -> ImageThumbnail:
        # Retrieve image from storage
        image_data: str = self.storage_service.retrieve_image_content_by_id(image_id)
        image: Image.Image = Image.open(BytesIO(base64.b64decode(image_data)))

        # Generate thumbnail
        thumbnail: Image.Image = image.copy()
        thumbnail.thumbnail(self.dimensions)

        # Create and return ImageThumbnail
        buffered = BytesIO()
        thumbnail.save(buffered, format=self.extension.upper())
        encoded_data = base64.b64encode(buffered.getvalue()).decode("utf-8") 
        thumbnail_base64 = f"{self.extension.to_base64_prefix()}{encoded_data}"

        # Create ImageThumbnail
        return ImageThumbnail.create(image_id=image_id, thumbnail_base64=thumbnail_base64)