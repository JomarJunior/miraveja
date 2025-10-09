from typing import Optional, Type
from Miraveja.Gallery.Domain.Interfaces import ILoraMetadataRepository
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.UnitOfWork.Domain.Interfaces import IUnitOfWorkFactory
from Miraveja.Shared.Utils.Types.Handler import HandlerResponse


class FindLoraMetadataByHashHandler:
    def __init__(
        self,
        databaseUOWFactory: IUnitOfWorkFactory,
        tLoraMetadataRepository: Type[ILoraMetadataRepository],
        logger: ILogger,
    ):
        self._databaseUOWFactory = databaseUOWFactory
        self._tLoraMetadataRepository = tLoraMetadataRepository
        self._logger = logger

    def Handle(self, hash: str) -> Optional[HandlerResponse]:
        self._logger.Info(f"Finding LoRA metadata by hash: {hash}")

        with self._databaseUOWFactory.Create() as unitOfWork:
            loraMetadata = unitOfWork.GetRepository(self._tLoraMetadataRepository).FindByHash(hash)
        if not loraMetadata:
            self._logger.Warning(f"LoRA metadata with hash {hash} not found.")
            return None

        self._logger.Info(f"LoRA metadata with hash {hash} found: {loraMetadata.model_dump_json(indent=4)}")
        return loraMetadata.model_dump()
