from typing import Type

from pydantic import BaseModel, Field

from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse
from MiravejaCore.Shared.VectorDatabase.Domain.Interfaces import IVectorDatabaseManagerFactory
from MiravejaCore.Vector.Domain.Enums import VectorType
from MiravejaCore.Vector.Domain.Interfaces import IVectorRepository
from MiravejaCore.Vector.Domain.Services import VectorGenerationService


class SearchVectorsByTextCommand(BaseModel):
    text: str = Field(..., description="The text to search vectors for")
    topK: int = Field(..., description="The number of top similar vectors to retrieve")
    vectorType: VectorType = Field(..., description="The type of vectors to search (e.g., IMAGE, TEXT)")


class SearchVectorsByTextHandler:
    def __init__(
        self,
        vectorDBFactory: IVectorDatabaseManagerFactory,
        tVectorRepository: Type[IVectorRepository],
        vectorGenerationService: VectorGenerationService,
        logger: ILogger,
    ):
        self.vectorDBFactory = vectorDBFactory
        self.tVectorRepository = tVectorRepository
        self.vectorGenerationService = vectorGenerationService
        self.logger = logger

    async def Handle(self, command: SearchVectorsByTextCommand) -> HandlerResponse:
        self.logger.Info(f"Handling SearchVectorsByTextCommand for text: {command.text}")
        with self.vectorDBFactory.Create() as dbManager:
            repository = dbManager.GetRepository(self.tVectorRepository)
            embedding = await self.vectorGenerationService.GenerateTextVector(command.text)
            self.logger.Debug(f"Generated embedding length: {embedding.size()}")
            results = await repository.SearchSimilar(
                embedding=embedding,
                topK=command.topK,
                vectorType=command.vectorType,
            )
            self.logger.Info(f"Found {len(results)} similar vectors for the given text.")
            return {"vectors": [vector.model_dump() for vector in results]}
