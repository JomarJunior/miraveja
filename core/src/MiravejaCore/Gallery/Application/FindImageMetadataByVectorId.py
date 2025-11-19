from typing import Type

from pydantic import BaseModel, Field

from MiravejaCore.Gallery.Domain.Interfaces import IImageMetadataRepository
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.Errors.Models import DomainException
from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse


class FindImageMetadataByVectorIdCommand(BaseModel):
    vectorId: VectorId = Field(..., description="The vector ID of the image metadata to find")


class FindImageMetadataByVectorIdHandler:
    def __init__(
        self,
        databaseManagerFactory: IDatabaseManagerFactory,
        tImageMetadataRepository: Type[IImageMetadataRepository],
        logger: ILogger,
    ):
        self._databaseManagerFactory = databaseManagerFactory
        self._tImageMetadataRepository = tImageMetadataRepository
        self._logger = logger

    def Handle(self, command: FindImageMetadataByVectorIdCommand) -> HandlerResponse:
        self._logger.Info(f"Finding image metadata by Vector ID: {command.vectorId.id}")

        with self._databaseManagerFactory.Create() as databaseManager:
            imageMetadata = databaseManager.GetRepository(self._tImageMetadataRepository).FindByVectorId(
                command.vectorId
            )
        if not imageMetadata:
            self._logger.Warning(f"Image metadata with Vector ID {command.vectorId.id} not found.")
            raise DomainException(f"Image metadata with Vector ID {command.vectorId.id} not found.")

        self._logger.Info(
            f"Image metadata with Vector ID {command.vectorId.id} found: {imageMetadata.model_dump_json(indent=4)}"
        )
        return imageMetadata.model_dump()
