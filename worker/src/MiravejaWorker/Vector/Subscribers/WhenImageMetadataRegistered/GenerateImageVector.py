from MiravejaCore.Gallery.Application.AddVectorIdToImageMetadata import (
    AddVectorIdToImageMetadataCommand,
    AddVectorIdToImageMetadataHandler,
)
from MiravejaCore.Gallery.Application.FindImageMetadataById import ImageMetadataId
from MiravejaCore.Gallery.Domain.Events import ImageMetadataRegisteredEvent
from MiravejaCore.Shared.Events.Domain.Interfaces import IEventSubscriber
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Vector.Application.GenerateImageVector import GenerateImageVectorCommand, GenerateImageVectorHandler

from MiravejaWorker.Shared.Storage.Domain.Interfaces import IImageContentProvider


class GenerateImageVector(IEventSubscriber[ImageMetadataRegisteredEvent]):
    def __init__(
        self,
        logger: ILogger,
        generateImageVectorHandler: GenerateImageVectorHandler,
        addVectorIdToImageMetadataHandler: AddVectorIdToImageMetadataHandler,
        imageContentProvider: IImageContentProvider,
    ):
        self._logger = logger
        self._generateImageVectorHandler = generateImageVectorHandler
        self._addVectorIdToImageMetadataHandler = addVectorIdToImageMetadataHandler
        self._imageContentProvider = imageContentProvider

    async def Handle(self, event: ImageMetadataRegisteredEvent) -> None:
        self._logger.Info(f"Handling ImageMetadataRegisteredEvent with ID: {event.id}")

        # Get the image content from the provided URI
        imageUri = event.data.get("uri")
        if imageUri is None:
            self._logger.Error(f"Image URI is missing in event data for ID: {event.id}")
            return
        imageContent = await self._imageContentProvider.GetImageContentFromUri(imageUri)

        # Generate the image vector using the image content
        generateVectorCommand = GenerateImageVectorCommand(
            imageData=imageContent,
        )
        vectorId = (await self._generateImageVectorHandler.Handle(generateVectorCommand)).get("vectorId")
        if vectorId is None:
            self._logger.Error(f"Failed to generate vector for ImageMetadataRegisteredEvent with ID: {event.id}")
            return

        # Update the image metadata with the generated vector ID
        addVectorCommand = AddVectorIdToImageMetadataCommand(
            vectorId=vectorId,
        )
        await self._addVectorIdToImageMetadataHandler.Handle(
            ImageMetadataId(id=event.imageMetadataId), addVectorCommand
        )

        self._logger.Info(f"Completed handling ImageMetadataRegisteredEvent with ID: {event.id}")
