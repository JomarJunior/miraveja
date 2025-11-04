from typing import Optional, Type

from MiravejaCore.Gallery.Domain.Exceptions import ImageMetadataNotFoundException
from MiravejaCore.Gallery.Domain.Interfaces import IImageMetadataRepository
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse


class FindImageMetadataByIdHandler:
    def __init__(
        self,
        databaseManagerFactory: IDatabaseManagerFactory,
        tImageMetadataRepository: Type[IImageMetadataRepository],
        logger: ILogger,
    ):
        self._databaseManagerFactory = databaseManagerFactory
        self._tImageMetadataRepository = tImageMetadataRepository
        self._logger = logger

    def Handle(self, imageMetadataId: ImageMetadataId) -> Optional[HandlerResponse]:
        self._logger.Info(f"Finding image metadata by ID: {imageMetadataId.id}")

        with self._databaseManagerFactory.Create() as databaseManager:
            imageMetadata = databaseManager.GetRepository(self._tImageMetadataRepository).FindById(imageMetadataId)
        if not imageMetadata:
            self._logger.Warning(f"Image metadata with ID {imageMetadataId.id} not found.")
            raise ImageMetadataNotFoundException(imageMetadataId)

        self._logger.Info(
            f"Image metadata with ID {imageMetadataId.id} found: {imageMetadata.model_dump_json(indent=4)}"
        )
        return imageMetadata.model_dump()
