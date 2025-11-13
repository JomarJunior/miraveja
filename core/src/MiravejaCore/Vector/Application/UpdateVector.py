from typing import Type

from pydantic import BaseModel
from torch import Tensor

from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.VectorDatabase.Domain.Interfaces import IVectorDatabaseManagerFactory
from MiravejaCore.Vector.Domain.Interfaces import IVectorRepository
from MiravejaCore.Vector.Domain.Models import Vector


class UpdateVectorCommand(BaseModel):
    vectorId: VectorId
    newEmbedding: Tensor

    model_config = {"arbitrary_types_allowed": True}


class UpdateVectorHandler:
    def __init__(
        self,
        vectorDBFactory: IVectorDatabaseManagerFactory,
        tVectorRepository: Type[IVectorRepository],
        logger: ILogger,
        eventDispatcher: EventDispatcher,
    ):
        self.vectorDBFactory = vectorDBFactory
        self.tVectorRepository = tVectorRepository
        self.logger = logger
        self.eventDispatcher = eventDispatcher

    async def Handle(self, command: UpdateVectorCommand) -> None:
        self.logger.Info(f"Handling UpdateVectorCommand for vector {command.vectorId}.")
        with self.vectorDBFactory.Create() as dbManager:
            repository = dbManager.GetRepository(self.tVectorRepository)
            vector: Vector = await repository.FindById(command.vectorId)
            vector.UpdateEmbedding(command.newEmbedding)
            await repository.Save(vector)
        self.logger.Info(f"Vector {command.vectorId} embedding updated.")
        await self.eventDispatcher.DispatchAll(vector.ReleaseEvents())
