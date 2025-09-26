"""
Internal services for the processing domain.
"""

from typing import Any, Dict
from src.Processing.Domain.Interfaces import IStorageService
from src.Storage.Application.Commands import DownloadImageContentCommand
from src.Storage.Application.Handlers import DownloadImageContentHandler

class InternalStorageService(IStorageService):
    """
    Internal implementation of the storage service.
    """
    def __init__(
            self,
            download_image_content_handler: DownloadImageContentHandler
    ):
        self.download_image_content_handler = download_image_content_handler

    def retrieve_image_content_by_id(self, image_id: int) -> str:
        command: DownloadImageContentCommand = DownloadImageContentCommand.from_dict({"id": image_id})
        result: Dict[str, Any] = self.download_image_content_handler.handle(command)
        return result.get("content", "")