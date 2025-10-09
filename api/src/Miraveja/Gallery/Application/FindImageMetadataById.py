from typing import Optional, Type

from Miraveja.Gallery.Domain.Exceptions import ImageMetadataNotFoundException
from Miraveja.Gallery.Domain.Interfaces import IImageMetadataRepository
from Miraveja.Shared.Identifiers.Models import ImageMetadataId
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.UnitOfWork.Domain.Interfaces import IUnitOfWorkFactory
from Miraveja.Shared.Utils.Types.Handler import HandlerResponse


class FindImageMetadataByIdHandler:
    def __init__(
        self,
        databaseUOWFactory: IUnitOfWorkFactory,
        tImageMetadataRepository: Type[IImageMetadataRepository],
        logger: ILogger,
    ):
        self._databaseUOWFactory = databaseUOWFactory
        self._tImageMetadataRepository = tImageMetadataRepository
        self._logger = logger

    def Handle(self, imageMetadataId: ImageMetadataId) -> Optional[HandlerResponse]:
        self._logger.Info(f"Finding image metadata by ID: {imageMetadataId.id}")

        with self._databaseUOWFactory.Create() as unitOfWork:
            imageMetadata = unitOfWork.GetRepository(self._tImageMetadataRepository).FindById(imageMetadataId)
        if not imageMetadata:
            self._logger.Warning(f"Image metadata with ID {imageMetadataId.id} not found.")
            raise ImageMetadataNotFoundException(imageMetadataId)

        self._logger.Info(
            f"Image metadata with ID {imageMetadataId.id} found: {imageMetadata.model_dump_json(indent=4)}"
        )
        return imageMetadata.model_dump()
