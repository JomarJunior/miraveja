"""
Image acquisition services.
"""

from src.Acquisition.Domain.Interfaces import IImageDownloader, IImageProvider
from src.Core.Events.Bus import EventEmitter
from src.Acquisition.Domain.Events import ManyImagesAcquiredEvent
from src.Acquisition.Domain.Models import Image, ImageContent
from typing import List, Tuple

class ImageAcquisitionService(EventEmitter):
    def __init__(self, image_provider: IImageProvider, image_downloader: IImageDownloader):
        super().__init__()
        self.image_provider = image_provider
        self.image_downloader = image_downloader

    def acquire_images(self, amount: int, cursor: str) -> Tuple[List[Image], List[ImageContent]]:
        """
        Acquire a specified amount of images.
        Returns a tuple of (image data, image content)
        """
        images = self.image_provider.get_images(amount, cursor)
        image_contents = [self.image_downloader.download_image(image) for image in images]

        self.emit_event(ManyImagesAcquiredEvent(images))
        return images, image_contents
