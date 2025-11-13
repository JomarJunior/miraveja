from typing import List, Type

from pydantic import BaseModel, model_validator

from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.VectorDatabase.Domain.Interfaces import IVectorDatabaseManagerFactory
from MiravejaCore.Vector.Domain.Exceptions import VectorsAndWeightsMismatchException
from MiravejaCore.Vector.Domain.Interfaces import IVectorRepository


class MergeVectorsCommand(BaseModel):
    """
    Command to merge multiple vectors into one.
    The first vector in the list is considered the main vector, which will absorb the others.
    The weights list must match the length of the vectors list.
    """

    vectors: List[VectorId]
    weights: List[float]

    @model_validator(mode="before")
    def ValidateLengths(cls, values):
        vectors = values.get("vectors", [])
        weights = values.get("weights", [])
        if len(vectors) != len(weights):
            raise VectorsAndWeightsMismatchException(len(vectors), len(weights))
        return values


class MergeVectorsHandler:
    """
    Handler for merging vectors.
    Merges multiple vectors into a single vector using specified weights.
    The merged vector is saved to the repository and relevant events are dispatched.
    The first vector in the list is treated as the main vector and will be updated with the merged result.
    """

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

    async def Handle(self, command: MergeVectorsCommand) -> None:
        self.logger.Info("Handling MergeVectorsCommand.")

        with self.vectorDBFactory.Create() as dbManager:
            repository = dbManager.GetRepository(self.tVectorRepository)
            vectors = await repository.FindManyByIds(command.vectors)
            merged = vectors[0].MergeWith(vectors[1:], command.weights)  # Order preserved by FindManyByIds
            await repository.Save(merged)

        await self.eventDispatcher.DispatchAll(merged.ReleaseEvents())

        self.logger.Info("Vectors merged.")
