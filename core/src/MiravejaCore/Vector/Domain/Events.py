from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent
from MiravejaCore.Shared.Events.Domain.Services import eventRegistry
from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Vector.Domain.Enums import VectorType


@eventRegistry.RegisterEvent("vector.created", 1)
class VectorCreatedEvent(DomainEvent):
    type = "vector.created"
    version = 1
    vectorId: VectorId
    vectorType: VectorType

    @classmethod
    def FromModel(cls, vector) -> "VectorCreatedEvent":
        return cls(
            aggregateId=str(vector.id),
            aggregateType="vector",
            vectorId=vector.id,
            vectorType=vector.type,
        )


@eventRegistry.RegisterEvent("vector.updated", 1)
class VectorUpdatedEvent(DomainEvent):
    type = "vector.updated"
    version = 1
    vectorId: VectorId
    vectorType: VectorType
    similarity: float

    @classmethod
    def FromModel(cls, vector, similarity: float) -> "VectorUpdatedEvent":
        return cls(
            aggregateId=str(vector.id),
            aggregateType="vector",
            vectorId=vector.id,
            vectorType=vector.type,
            similarity=similarity,
        )


@eventRegistry.RegisterEvent("vector.merged", 1)
class VectorsMergedEvent(DomainEvent):
    type = "vector.merged"
    version = 1
    vectorId: VectorId
    vectorType: VectorType
    sourceVectorIds: list[VectorId]

    @classmethod
    def FromModel(cls, vector, sourceVectors) -> "VectorsMergedEvent":
        return cls(
            aggregateId=str(vector.id),
            aggregateType="vector",
            vectorId=vector.id,
            vectorType=vector.type,
            sourceVectorIds=[v.id for v in sourceVectors],
        )
