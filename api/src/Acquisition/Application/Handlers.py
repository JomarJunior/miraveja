"""
Use case handlers for image acquisition.
"""

from src.Acquisition.Application.Commands import AcquireImageCommand
from src.Acquisition.Domain.Interfaces import IStorageService
from src.Acquisition.Domain.Models import Image, ImageContent
from src.Acquisition.Domain.Services import ImageAcquisitionService
from src.Core.Events.Bus import EventDispatcher
from src.Core.Logging.Logger import Logger
from src.Core.Tasks.TaskManager import TaskManager
from typing import Any, Dict, List

    
class AcquireImageHandler:
    def __init__(
            self,
            image_acquisition_service: ImageAcquisitionService,
            storage_service: IStorageService,
            event_dispatcher: EventDispatcher,
            task_manager: TaskManager,
            logger: Logger
        ):
        self.image_acquisition_service = image_acquisition_service
        self.storage_service = storage_service
        self.event_dispatcher = event_dispatcher
        self.task_manager = task_manager
        self.logger = logger

    def handle(self, command: AcquireImageCommand) -> Dict[str, Any]:
        """
        Handle the image acquisition command.
        """
        # Use the TaskManager to execute the operation
        task_result = self.task_manager.execute(
            self._acquire_images,
            command.amount,
            command.cursor,
            detached=command.detached,
        )
        return task_result.to_dict()

    def _acquire_images(self, amount: int, cursor: str) -> Dict[str, Any]:
        # Log the acquisition attempt
        self.logger.info(f"Acquiring {amount} images.")
        images, image_contents = self.image_acquisition_service.acquire_images(amount=amount, cursor=cursor)

        acquired_images_amount = len(images)
        acquired_image_contents_amount = len(image_contents)

        self.logger.info(f"Acquired {acquired_images_amount} images.")
        self.logger.info(f"Acquired {acquired_image_contents_amount} image contents.")

        if acquired_images_amount != acquired_image_contents_amount:
            self.logger.error("Mismatch between acquired images and image contents.")

        # Save images and their contents
        image_ids: List[int] = []
        image_uris: List[str] = []
        for image, content in zip(images, image_contents):
            if content is not None:
                image_id, image_uri = self.storage_service.save_image_and_content(image, content)
                image_ids.append(image_id)
                image_uris.append(image_uri)

        self.event_dispatcher.dispatch_all(self.image_acquisition_service.release_events())

        # Dispatch individual image release events
        for image in images:
            self.event_dispatcher.dispatch_all(image.release_events())

        return {
            "acquired_images": acquired_images_amount,
            "acquired_image_contents": acquired_image_contents_amount,
            "image_ids": image_ids,
            "image_uris": image_uris,
        }

