from typing import Optional, Type
from pydantic import BaseModel, Field

from Miraveja.Gallery.Domain.Interfaces import ILoraMetadataRepository
from Miraveja.Gallery.Domain.Models import LoraMetadata
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.UnitOfWork.Domain.Interfaces import IUnitOfWorkFactory


class RegisterLoraMetadataCommand(BaseModel):
    hash: str = Field(..., description="Hash of the LoRA")
    name: Optional[str] = Field(None, description="Name of the LoRA")


class RegisterLoraMetadataHandler:
    def __init__(
        self,
        databaseUOWFactory: IUnitOfWorkFactory,
        tLoraMetadataRepository: Type[ILoraMetadataRepository],
        logger: ILogger,
    ):
        self._databaseUOWFactory = databaseUOWFactory
        self._tLoraMetadataRepository = tLoraMetadataRepository
        self._logger = logger

    def Handle(self, command: RegisterLoraMetadataCommand) -> int:
        self._logger.Info(f"Registering LoRA metadata with command: {command.model_dump_json(indent=4)}")

        with self._databaseUOWFactory.Create() as unitOfWork:
            loraMetadataId = unitOfWork.GetRepository(self._tLoraMetadataRepository).GenerateNewId()

            self._logger.Debug(f"Creating LoRA metadata entity with ID: {loraMetadataId}")

            loraMetadata = LoraMetadata.Register(id=loraMetadataId, hash=command.hash, name=command.name)

            unitOfWork.GetRepository(self._tLoraMetadataRepository).Save(loraMetadata)
            unitOfWork.Commit()

        self._logger.Info(f"LoRA metadata registered with ID: {loraMetadataId}")

        return loraMetadataId.id
