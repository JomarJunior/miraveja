from typing import Type, Optional

from pydantic import BaseModel, Field

from MiravejaCore.Gallery.Domain.Exceptions import ImageMetadataNotFoundException
from MiravejaCore.Gallery.Domain.Interfaces import IImageMetadataRepository
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId, VectorId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory


class UpdateImageMetadataCommand(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New title of the image")
    subtitle: Optional[str] = Field(None, min_length=1, max_length=200, description="New subtitle of the image")
    description: Optional[str] = Field(None, max_length=2000, description="New description of the image")
    vectorId: Optional[int] = Field(None, description="New vector ID to assign to the image")
    removeVectorId: bool = Field(False, description="Flag to remove the vector ID from the image")


class UpdateImageMetadataHandler:
    def __init__(
        self,
        databaseUOWFactory: IDatabaseManagerFactory,
        tImageMetadataRepository: Type[IImageMetadataRepository],
        eventDispatcher: EventDispatcher,
        logger: ILogger,
    ):
        self._databaseUOWFactory = databaseUOWFactory
        self._tImageMetadataRepository = tImageMetadataRepository
        self._eventDispatcher = eventDispatcher
        self._logger = logger

    async def Handle(self, imageMetadataId: ImageMetadataId, command: UpdateImageMetadataCommand) -> None:
        self._logger.Info(f"Updating image metadata with command: {command.model_dump_json(indent=4)}")

        with self._databaseUOWFactory.Create() as databaseManager:
            repository = databaseManager.GetRepository(self._tImageMetadataRepository)
            imageMetadata = repository.FindById(imageMetadataId)

            if not imageMetadata:
                self._logger.Warning(f"Image metadata with ID {imageMetadataId.id} not found.")
                raise ImageMetadataNotFoundException(imageMetadataId)

            # Update fields if any text field is provided
            if command.title is not None or command.subtitle is not None or command.description is not None:
                imageMetadata.Update(
                    title=command.title if command.title is not None else imageMetadata.title,
                    subtitle=command.subtitle if command.subtitle is not None else imageMetadata.subtitle,
                    description=command.description if command.description is not None else imageMetadata.description,
                )

            # Handle vector ID operations
            if command.removeVectorId:
                if imageMetadata.vectorId is not None:
                    self._logger.Debug(f"Removing vector ID {imageMetadata.vectorId.id} from image metadata")
                    imageMetadata.UnassignVectorId()
                else:
                    self._logger.Debug("No vector ID to remove from image metadata")
            elif command.vectorId is not None:
                vectorId = VectorId(id=command.vectorId)
                self._logger.Debug(f"Assigning vector ID {vectorId.id} to image metadata")
                imageMetadata.AssignVectorId(vectorId)

            repository.Save(imageMetadata)
            databaseManager.Commit()

        self._logger.Info(f"Image metadata updated successfully: {imageMetadata.model_dump_json(indent=4)}")
        await self._eventDispatcher.DispatchAll(imageMetadata.ReleaseEvents())
