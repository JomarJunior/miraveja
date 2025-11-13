from io import BytesIO
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


class GenerateImageVectorCommand(BaseModel):
    imageData: bytes


class GenerateImageVectorHandler:
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

    async def Handle(self, command: GenerateImageVectorCommand) -> HandlerResponse:
        self.logger.Info("Handling GenerateImageVectorCommand.")
        embedding = await self.vectorGenerationService.GenerateImageVector(BytesIO(command.imageData))
        self.logger.Info("Image vector generated.")

        newId: VectorId = VectorId.Generate()
        vector = Vector.Create(id=newId, type=VectorType.IMAGE, embedding=embedding)

        with self.vectorDBFactory.Create() as dbManager:
            self.logger.Info("Saving vector to repository.")
            repository = dbManager.GetRepository(self.tVectorRepository)
            self.logger.Info(f"Saving vector with ID {newId} to repository.")
            await repository.Save(vector)

        self.logger.Info(f"Vector {newId} saved to repository.")
        await self.eventDispatcher.DispatchAll(vector.ReleaseEvents())

        return {"vectorId": newId}
