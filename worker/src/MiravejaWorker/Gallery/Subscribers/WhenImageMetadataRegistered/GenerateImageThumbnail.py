from MiravejaCore.Gallery.Application.AddThumbnailToImageMetadata import AddThumbnailToImageMetadataCommand
from MiravejaCore.Gallery.Application.GenerateThumbnail import GenerateThumbnailCommand, GenerateThumbnailHandler
from MiravejaCore.Gallery.Domain.Events import ImageMetadataRegisteredEvent
from MiravejaCore.Gallery.Infrastructure.GalleryDependencies import AddThumbnailToImageMetadataHandler
from MiravejaCore.Shared.Events.Domain.Interfaces import IEventSubscriber
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger

from MiravejaWorker.Shared.Storage.Domain.Interfaces import IImageContentProvider


class GenerateImageThumbnail(IEventSubscriber[ImageMetadataRegisteredEvent]):
    def __init__(
        self,
        logger: ILogger,
        generateThumbnailHandler: GenerateThumbnailHandler,
        addThumbnailToImageMetadataHandler: AddThumbnailToImageMetadataHandler,
        imageContentProvider: IImageContentProvider,
    ):
        self._logger = logger
        self._generateThumbnailHandler = generateThumbnailHandler
        self._addThumbnailToImageMetadataHandler = addThumbnailToImageMetadataHandler
        self._imageContentProvider = imageContentProvider

    async def Handle(self, event: ImageMetadataRegisteredEvent) -> None:
        self._logger.Info(f"Handling ImageMetadataRegisteredEvent with ID: {event.id}")

        # Get the image content from the provided URI
        imageUri = event.data.get("uri")
        if imageUri is None:
            self._logger.Error(f"Image URI is missing in event data for ID: {event.id}")
            return
        imageContent = await self._imageContentProvider.GetImageContentFromUri(imageUri)

        # Generate the thumbnail using the image content
        ownerIdStr = event.data.get("ownerId")
        if ownerIdStr is None:
            self._logger.Error(f"Owner ID is missing in event data for ID: {event.id}")
            return

        generateThumbnailCommand = GenerateThumbnailCommand(
            imageData=imageContent,
            ownerId=MemberId(id=ownerIdStr),
        )
        thumbnailUri = await self._generateThumbnailHandler.Handle(generateThumbnailCommand)

        self._logger.Debug(f"Generated thumbnail URI: {thumbnailUri}")

        # Update the image metadata with the generated thumbnail
        addThumbnailCommand: AddThumbnailToImageMetadataCommand = AddThumbnailToImageMetadataCommand(
            thumbnailUri=thumbnailUri,
        )
        await self._addThumbnailToImageMetadataHandler.Handle(event.imageMetadataId, addThumbnailCommand)

        self._logger.Info(f"Completed handling ImageMetadataRegisteredEvent with ID: {event.id}")
