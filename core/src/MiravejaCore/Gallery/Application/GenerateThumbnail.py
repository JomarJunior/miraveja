from io import BytesIO
from uuid import uuid4

from pydantic import BaseModel

from MiravejaCore.Gallery.Domain.Interfaces import IImageContentRepository, IThumbnailGenerationService
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class GenerateThumbnailCommand(BaseModel):
    imageData: bytes
    ownerId: MemberId


class GenerateThumbnailHandler:
    def __init__(
        self,
        thumbnailGenerationService: IThumbnailGenerationService,
        imageContentRepository: IImageContentRepository,
        logger: ILogger,
        eventDispatcher: EventDispatcher,
    ):
        self.thumbnailGenerationService = thumbnailGenerationService
        self.imageContentRepository = imageContentRepository
        self.logger = logger
        self.eventDispatcher = eventDispatcher

    async def Handle(self, command: GenerateThumbnailCommand) -> str:
        self.logger.Info("Handling GenerateThumbnailCommand.")
        thumbnailData = await self.thumbnailGenerationService.GenerateThumbnail(BytesIO(command.imageData))
        self.logger.Info("Thumbnail generated.")

        key: str = (
            f"{str(command.ownerId)}/thumbnails/{str(uuid4())}.{self.thumbnailGenerationService.format.ToExtension()}"
        )

        uri = await self.imageContentRepository.Upload(
            key=key,
            imageContent=thumbnailData,
        )

        self.logger.Info(f"Thumbnail uploaded to {uri}.")

        return uri
