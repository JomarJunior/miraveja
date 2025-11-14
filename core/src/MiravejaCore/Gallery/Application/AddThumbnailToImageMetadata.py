from pydantic import BaseModel, Field

from MiravejaCore.Gallery.Domain.Exceptions import ImageMetadataNotFoundException
from MiravejaCore.Gallery.Domain.Models import ImageMetadata


class AddThumbnailToImageMetadataCommand(BaseModel):
    thumbnailUri: str = Field(..., description="New thumbnail URI to assign to the image")


class AddThumbnailToImageMetadataHandler:
    def __init__(
        self,
        databaseManagerFactory,
        tImageMetadataRepository,
        eventDispatcher,
        logger,
    ):
        self._databaseManagerFactory = databaseManagerFactory
        self._tImageMetadataRepository = tImageMetadataRepository
        self._eventDispatcher = eventDispatcher
        self._logger = logger

    async def Handle(self, imageMetadataId, command: AddThumbnailToImageMetadataCommand) -> None:
        self._logger.Info(f"Adding thumbnail to image metadata with command: {command.model_dump_json(indent=4)}")

        with self._databaseManagerFactory.Create() as databaseManager:
            repository = databaseManager.GetRepository(self._tImageMetadataRepository)
            imageMetadata: ImageMetadata = repository.FindById(imageMetadataId)

            if not imageMetadata:
                self._logger.Warning(f"Image metadata with ID {imageMetadataId.id} not found.")
                raise ImageMetadataNotFoundException(imageMetadataId)

            self._logger.Debug(f"Assigning thumbnail URI {command.thumbnailUri} to image metadata")
            imageMetadata.SetThumbnailUri(command.thumbnailUri)

            repository.Save(imageMetadata)
            databaseManager.Commit()

        self._logger.Info(f"Image metadata updated successfully: {imageMetadata.model_dump_json(indent=4)}")
        await self._eventDispatcher.DispatchAll(imageMetadata.ReleaseEvents())
