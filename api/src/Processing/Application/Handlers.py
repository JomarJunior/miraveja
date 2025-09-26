"""
Use case handlers for image processing.
"""

from typing import Any, Dict
from src.Processing.Domain.Models import (
    ImageEmbedding,
    TextEmbedding,
    ImageThumbnail
)
from src.Processing.Domain.Interfaces import (
    IEmbeddingsGenerationService,
    IThumbnailService,
    IStorageService
)
from src.Processing.Domain.Enums import DistanceMetricEnum
from src.Processing.Application.Commands import (
    GetTextEmbeddingCommand,
    GetImageEmbeddingCommand,
    GetImageThumbnailCommand
)
from src.Core.Events.Bus import EventDispatcher
from src.Core.Logging.Logger import Logger
from src.Core.Tasks.TaskManager import TaskManager

class GetTextEmbeddingHandler:
    def __init__(
            self,
            embeddings_generation_service: IEmbeddingsGenerationService,
            task_manager: TaskManager,
            storage_service: IStorageService,
            event_dispatcher: EventDispatcher,
            logger: Logger,
    ):
        self.embeddings_generation_service = embeddings_generation_service
        self.task_manager = task_manager
        self.storage_service = storage_service
        self.event_dispatcher = event_dispatcher
        self.logger = logger

    def handle(self, command: GetTextEmbeddingCommand) -> Dict[str, Any]:
        task_result = self.task_manager.execute(
            self._generate_and_save_text_embedding,
            command.text,
            detached=command.detached,
        )
        return task_result.to_dict()
    
    def _generate_and_save_text_embedding(self, text: str) -> TextEmbedding:
        self.logger.info(f"Generating text embedding for: {text}")
        embedding = self.embeddings_generation_service.generate_text_embedding(text)

        self.logger.info(f"Generated text embedding, saving...")
        self.storage_service.save_text_embedding(embedding)

        self.logger.info(f"Text embedding saved, emitting event...")
        self.event_dispatcher.dispatch_all(embedding.release_events())
        return embedding

class GetImageEmbeddingHandler:
    def __init__(
            self,
            embeddings_generation_service: IEmbeddingsGenerationService,
            task_manager: TaskManager,
            storage_service: IStorageService,
            event_dispatcher: EventDispatcher,
            logger: Logger,
    ):
        self.embeddings_generation_service = embeddings_generation_service
        self.task_manager = task_manager
        self.storage_service = storage_service
        self.event_dispatcher = event_dispatcher
        self.logger = logger

    def handle(self, command: GetImageEmbeddingCommand) -> Dict[str, Any]:
        task_result = self.task_manager.execute(
            self._generate_and_save_image_embedding,
            command.image_id,
            detached=command.detached,
        )
        return task_result.to_dict()

    def _generate_and_save_image_embedding(self, image_id: int) -> ImageEmbedding:
        self.logger.info(f"Generating image embedding for image with id: {image_id}")
        embedding = self.embeddings_generation_service.generate_image_embedding(image_id)

        self.logger.info(f"Generated image embedding, saving...")
        self.storage_service.save_image_embedding(embedding)

        self.logger.info(f"Image embedding saved, emitting event...")
        self.event_dispatcher.dispatch_all(embedding.release_events())
        return embedding

class GetImageThumbnailHandler:
    def __init__(
            self,
            thumbnail_service: IThumbnailService,
            task_manager: TaskManager,
            storage_service: IStorageService,
            event_dispatcher: EventDispatcher,
            logger: Logger,
    ):
        self.thumbnail_service = thumbnail_service
        self.task_manager = task_manager
        self.storage_service = storage_service
        self.event_dispatcher = event_dispatcher
        self.logger = logger

    def handle(self, command: GetImageThumbnailCommand) -> Dict[str, Any]:
        task_result = self.task_manager.execute(
            self._generate_and_save_image_thumbnail,
            command.image_id,
            detached=command.detached,
        )
        return task_result.to_dict()

    def _generate_and_save_image_thumbnail(self, image_id: int) -> ImageThumbnail:
        self.logger.info(f"Generating image thumbnail for image with id: {image_id}")
        thumbnail = self.thumbnail_service.generate_image_thumbnail(image_id)

        self.logger.info(f"Generated image thumbnail, saving...")
        self.storage_service.save_image_thumbnail(thumbnail)

        self.logger.info(f"Image thumbnail saved, emitting event...")
        self.event_dispatcher.dispatch_all(thumbnail.release_events())
        return thumbnail