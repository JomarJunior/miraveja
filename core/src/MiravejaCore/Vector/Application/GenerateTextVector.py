from typing import Type

from pydantic import BaseModel

from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse
from MiravejaCore.Shared.VectorDatabase.Domain.Interfaces import IVectorDatabaseManagerFactory
from MiravejaCore.Vector.Domain.Interfaces import IVectorRepository
from MiravejaCore.Vector.Domain.Models import Vector, VectorType
from MiravejaCore.Vector.Domain.Services import VectorGenerationService


class GenerateTextVectorCommand(BaseModel):
    text: str


class GenerateTextVectorHandler:
    def __init__(
        self,
        vectorGenerationService: VectorGenerationService,
        vectorDBFactory: IVectorDatabaseManagerFactory,
        tVectorRepository: Type[IVectorRepository],
        logger: ILogger,
        eventDispatcher: EventDispatcher,
    ):
        self.vectorGenerationService = vectorGenerationService
        self.vectorDBFactory = vectorDBFactory
        self.tVectorRepository = tVectorRepository
        self.logger = logger
        self.eventDispatcher = eventDispatcher

    async def Handle(self, command: GenerateTextVectorCommand) -> HandlerResponse:
        self.logger.Info("Handling GenerateTextVectorCommand.")
        embedding = await self.vectorGenerationService.GenerateTextVector(command.text)
        self.logger.Info("Text vector generated.")

        newId: VectorId = VectorId.Generate()
        vector = Vector.Create(id=newId, type=VectorType.TEXT, embedding=embedding)

        with self.vectorDBFactory.Create() as dbManager:
            repository = dbManager.GetRepository(self.tVectorRepository)
            await repository.Save(vector)

        self.logger.Info(f"Vector {newId} saved to repository.")
        await self.eventDispatcher.DispatchAll(vector.ReleaseEvents())

        return {"vectorId": newId}
