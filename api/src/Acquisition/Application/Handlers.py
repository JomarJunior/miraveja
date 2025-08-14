"""
Use case handlers for image acquisition.
"""

from src.Acquisition.Application.Commands import AcquireImageCommand
from src.Acquisition.Domain.Models import Image, ImageContent
from src.Acquisition.Domain.Services import ImageAcquisitionService
from src.Core.Events.Bus import EventDispatcher
from src.Core.Logging.Logger import Logger
from typing import List, Tuple

class AcquireImageHandler:
    def __init__(
            self,
            image_acquisition_service: ImageAcquisitionService,
            event_dispatcher: EventDispatcher,
            logger: Logger
        ):
        self.image_acquisition_service = image_acquisition_service
        self.event_dispatcher = event_dispatcher
        self.logger = logger

    def handle(self, command: AcquireImageCommand) -> Tuple[List[Image], List[ImageContent]]:
        """
        Handle the image acquisition command.
        """
        # Log the acquisition attempt
        self.logger.info(f"Acquiring {command.amount} images.")
        images, image_contents = self.image_acquisition_service.acquire_images(command.amount)

        acquired_images_amount = len(images)
        acquired_image_contents_amount = len(image_contents)

        self.logger.info(f"Acquired {acquired_images_amount} images.")
        self.logger.info(f"Acquired {acquired_image_contents_amount} image contents.")

        if acquired_images_amount != acquired_image_contents_amount:
            self.logger.error("Mismatch between acquired images and image contents.")

        self.event_dispatcher.dispatch_all(self.image_acquisition_service.release_events())

        # Dispatch individual image release events
        for image in images:
            self.event_dispatcher.dispatch_all(image.release_events())

        # Return the acquired images
        return images, image_contents
