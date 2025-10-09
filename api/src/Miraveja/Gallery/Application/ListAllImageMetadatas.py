from typing import Type
from Miraveja.Gallery.Domain.Interfaces import IImageMetadataRepository
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.UnitOfWork.Domain.Interfaces import IUnitOfWorkFactory
from Miraveja.Shared.Utils.Repository.Queries import ListAllQuery
from Miraveja.Shared.Utils.Types.Handler import HandlerResponse


class ListAllImageMetadatasCommand(ListAllQuery):
    pass


class ListAllImageMetadatasHandler:
    def __init__(
        self,
        databaseUOWFactory: IUnitOfWorkFactory,
        tImageMetadataRepository: Type[IImageMetadataRepository],
        logger: ILogger,
    ):
        self._databaseUOWFactory = databaseUOWFactory
        self._tImageMetadataRepository = tImageMetadataRepository
        self._logger = logger

    def Handle(self, command: ListAllImageMetadatasCommand) -> HandlerResponse:
        self._logger.Info(f"Listing all image metadatas with command: {command.model_dump_json(indent=4)}")
        with self._databaseUOWFactory.Create() as unitOfWork:
            repository: IImageMetadataRepository = unitOfWork.GetRepository(self._tImageMetadataRepository)
            allImageMetadatas = repository.ListAll(command)
            totalImageMetadatas = repository.Count()

            imageMetadatas = list(map(lambda imageMetadata: imageMetadata.model_dump(), allImageMetadatas))
        return {
            "items": imageMetadatas,
            "pagination": {
                "total": totalImageMetadatas,
                "offset": command.offset if hasattr(command, "offset") else 0,
                "limit": command.limit if hasattr(command, "limit") else len(imageMetadatas),
            },
        }
