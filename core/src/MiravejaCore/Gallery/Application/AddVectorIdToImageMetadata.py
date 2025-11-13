from typing import Type

from pydantic import BaseModel, Field

from MiravejaCore.Gallery.Domain.Exceptions import ImageMetadataNotFoundException
from MiravejaCore.Gallery.Domain.Interfaces import IImageMetadataRepository
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId, VectorId
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class AddVectorIdToImageMetadataCommand(BaseModel):
    vectorId: VectorId = Field(..., description="New vector ID to assign to the image")


class AddVectorIdToImageMetadataHandler:
    def __init__(
        self,
        databaseManagerFactory: IDatabaseManagerFactory,
        tImageMetadataRepository: Type[IImageMetadataRepository],
        eventDispatcher: EventDispatcher,
        logger: ILogger,
    ):
        self._databaseManagerFactory = databaseManagerFactory
        self._tImageMetadataRepository = tImageMetadataRepository
        self._eventDispatcher = eventDispatcher
        self._logger = logger

    async def Handle(self, imageMetadataId: ImageMetadataId, command: AddVectorIdToImageMetadataCommand) -> None:
        self._logger.Info(f"Adding vector ID to image metadata with command: {command.model_dump_json(indent=4)}")

        with self._databaseManagerFactory.Create() as databaseManager:
            repository = databaseManager.GetRepository(self._tImageMetadataRepository)
            imageMetadata = repository.FindById(imageMetadataId)

            if not imageMetadata:
                self._logger.Warning(f"Image metadata with ID {imageMetadataId.id} not found.")
                raise ImageMetadataNotFoundException(imageMetadataId)

            self._logger.Debug(f"Assigning vector ID {command.vectorId.id} to image metadata")
            imageMetadata.AssignVectorId(command.vectorId)

            repository.Save(imageMetadata)
            databaseManager.Commit()

        self._logger.Info(f"Image metadata updated successfully: {imageMetadata.model_dump_json(indent=4)}")
        await self._eventDispatcher.DispatchAll(imageMetadata.ReleaseEvents())
