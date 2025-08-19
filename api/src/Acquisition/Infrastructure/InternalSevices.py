"""
Internal services are those that operate within the system's contexts.
"""

from typing import Tuple
from src.Acquisition.Domain.Models import Image, ImageContent
from src.Storage.Application.Commands import (UploadImageContentCommand, RegisterImageCommand)
from src.Storage.Application.Handlers import (UploadImageContentHandler, RegisterImageHandler)
from src.Acquisition.Domain.Interfaces import IStorageService

class InternalStorageService(IStorageService):
    """
    Internal storage service implementation.
    """
    def __init__(
            self,
            upload_image_content_handler: UploadImageContentHandler,
            register_image_handler: RegisterImageHandler
        ):
            self._upload_image_content_handler = upload_image_content_handler
            self._register_image_handler = register_image_handler

    def save_image_and_content(self, image: Image, content: ImageContent) -> Tuple[int, str]:
        upload_image_content_command = UploadImageContentCommand.from_dict(
            {
                    "content": content.base64_content
            }
        )
        image_uri = self._upload_image_content_handler.handle(upload_image_content_command)

        register_image_command = RegisterImageCommand.from_dict(
            {
                "image_uri": image_uri,
                "image_metadata": image.metadata,
                "provider_id": image.provider_id
            }
        )
        image_id = self._register_image_handler.handle(register_image_command)
        return image_id, image_uri
