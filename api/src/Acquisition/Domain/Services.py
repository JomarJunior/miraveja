"""
Image acquisition services.
"""

from src.Acquisition.Domain.Interfaces import IImageDownloader, IImageProvider
from src.Config.AppConfig import AppConfig
from src.Core.Events.Bus import EventEmitter
from src.Core.Logging.Logger import Logger
from src.Acquisition.Domain.Events import ManyImagesAcquiredEvent
from src.Acquisition.Domain.Models import Image, ImageContent
from typing import List, Optional, Tuple
import concurrent.futures

class ImageAcquisitionService(EventEmitter):
    def __init__(
                self,
                app_config: AppConfig,
                image_provider: IImageProvider,
                image_downloader: IImageDownloader,
                logger: Logger
        ):
        super().__init__()

        self.max_workers = app_config.max_workers
        self.image_provider = image_provider
        self.image_downloader = image_downloader
        self.logger = logger

    def acquire_images(self, amount: int, cursor: str) -> Tuple[List[Image], List[Optional[ImageContent]]]:
        """
        Acquire a specified amount of images.
        Returns a tuple of (image data, image content)
        """
        images = self.image_provider.get_images(amount, cursor)
        # image_contents = [self.image_downloader.download_image(image) for image in images]
        image_contents: List[Optional[ImageContent]] = [None] * len(images)  # Pre-allocate list for image contents

        # Use ThreadPoolExecutor to download images in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit download tasks
            future_to_index = {}
            for i, image in enumerate(images):
                future = executor.submit(self.image_downloader.download_image, image)
                future_to_index[future] = i

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    image_contents[index] = future.result()
                except Exception as error:
                    # Log the error but continue processing other images
                    self.logger.error(f"Error downloading image {images[index].to_dict()}: {error}")
                    # Keep None at this position in image_contents

        self.emit_event(ManyImagesAcquiredEvent(images))
        return images, image_contents
