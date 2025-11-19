from typing import Type

from pydantic import BaseModel, Field

from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse
from MiravejaCore.Shared.VectorDatabase.Domain.Interfaces import IVectorDatabaseManagerFactory
from MiravejaCore.Vector.Domain.Exceptions import VectorNotFoundException
from MiravejaCore.Vector.Domain.Interfaces import IVectorRepository


class FindVectorByIdCommand(BaseModel):
    vectorId: VectorId = Field(..., description="The unique identifier of the vector to find")


class FindVectorByIdHandler:
    def __init__(
        self,
        vectorDBFactory: IVectorDatabaseManagerFactory,
        tVectorRepository: Type[IVectorRepository],
        logger: ILogger,
    ):
        self.vectorDBFactory = vectorDBFactory
        self.tVectorRepository = tVectorRepository
        self.logger = logger

    async def Handle(self, command: FindVectorByIdCommand) -> HandlerResponse:
        self.logger.Info(f"Handling FindVectorByIdCommand for Vector ID: {command.vectorId}")
        with self.vectorDBFactory.Create() as dbManager:
            repository = dbManager.GetRepository(self.tVectorRepository)
            vector = await repository.FindById(command.vectorId)
            if vector:
                self.logger.Info(f"Vector with ID {command.vectorId} found.")
            else:
                self.logger.Info(f"Vector with ID {command.vectorId} not found.")
                raise VectorNotFoundException(f"Vector with ID {command.vectorId} not found.")
            return vector.model_dump()
