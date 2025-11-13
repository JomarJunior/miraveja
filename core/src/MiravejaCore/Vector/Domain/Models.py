from datetime import datetime, timezone
from typing import List, Literal

import torch
from pydantic import Field, field_serializer, field_validator
from torch import Tensor

from MiravejaCore.Shared.Events.Domain.Models import EventEmitter
from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Vector.Domain.Enums import VectorType
from MiravejaCore.Vector.Domain.Events import VectorCreatedEvent, VectorsMergedEvent, VectorUpdatedEvent
from MiravejaCore.Vector.Domain.Exceptions import (
    EmbeddingMustBeNormalizedException,
    EmbeddingMustBeOneDimensionalException,
    EmbeddingOnCUDANotSupportedException,
    VectorsDimensionMismatchException,
)


class Vector(EventEmitter):
    id: VectorId = Field(..., description="The unique identifier of the vector.")
    type: VectorType = Field(..., description="The type of the vector.")
    embedding: Tensor = Field(
        ...,
        description="The vector embedding as a 1D tensor.",
    )  # * pydantic Arbitrary Type
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "arbitrary_types_allowed": True,  # * Allow non-pydantic types like torch.Tensor
    }

    @property
    def dimension(self) -> int:
        return self.embedding.shape[0]

    @property
    def device(self) -> torch.device:
        return self.embedding.device

    @field_validator("embedding", mode="before")
    def ValidateEmbedding(cls, value: Tensor) -> Tensor:
        if value.ndim != 1:
            raise EmbeddingMustBeOneDimensionalException(value.ndim)

        normalized = value / value.norm()
        if not torch.isclose(normalized.norm(), torch.tensor(1.0)):
            raise EmbeddingMustBeNormalizedException(normalized.norm().item())

        return value

    @field_serializer("createdAt", "updatedAt")
    def SerializeTimestamps(self, value: datetime) -> str:
        return value.isoformat()

    @field_serializer("embedding")
    def SerializeEmbedding(self, value: Tensor) -> list[float]:
        return value.tolist()

    @classmethod
    def Create(cls, id: VectorId, type: VectorType, embedding: Tensor) -> "Vector":
        vector = cls(id=id, type=type, embedding=embedding)
        vector.EmitEvent(VectorCreatedEvent.FromModel(vector))
        return vector

    @classmethod
    def FromDatabase(
        cls, id: str, type: str, embedding: list[float], createdAt: datetime, updatedAt: datetime
    ) -> "Vector":
        return cls(
            id=VectorId(id=id),
            type=VectorType(type),
            embedding=Tensor(embedding),
            createdAt=createdAt,
            updatedAt=updatedAt,
        )

    def Normalized(self) -> "Vector":
        normalizedEmbedding = self.embedding / self.embedding.norm()
        return Vector(
            id=self.id,
            type=self.type,
            embedding=normalizedEmbedding,
            createdAt=self.createdAt,
            updatedAt=self.updatedAt,
        )

    def CalculateSimilarity(self, other: "Vector") -> float:
        """Calculate the cosine similarity between this vector and another vector."""
        if self.dimension != other.dimension:
            raise VectorsDimensionMismatchException(self.dimension, other.dimension)

        similarity = self.CalculateSimilarityToEmbedding(other.embedding)
        return similarity

    def CalculateSimilarityToEmbedding(self, otherEmbedding: Tensor) -> float:
        """Calculate the cosine similarity between this vector and another embedding."""
        if self.dimension != otherEmbedding.shape[0]:
            raise VectorsDimensionMismatchException(self.dimension, otherEmbedding.shape[0])

        similarity = torch.dot(self.embedding, otherEmbedding) / (self.embedding.norm() * otherEmbedding.norm())
        return similarity.item()

    def MergeWith(self, others: List["Vector"], weights: List[float]) -> "Vector":
        """Merge this vector with other vectors using the provided weights."""
        if len(others) == 0:
            return self  # Nothing to merge

        allVectors = [self] + others

        if len(allVectors) != len(weights):
            raise VectorsDimensionMismatchException(len(allVectors), len(weights))

        for vec in allVectors:
            if vec.dimension != self.dimension:
                raise VectorsDimensionMismatchException(self.dimension, vec.dimension)

        mergedEmbedding = sum(vec.embedding * weight for vec, weight in zip(allVectors, weights))

        if mergedEmbedding == 0:
            mergedEmbedding = torch.zeros_like(self.embedding, device=self.embedding.device)

        # Ensure the merged embedding is normalized
        mergedEmbedding = mergedEmbedding / mergedEmbedding.norm()

        mergedVector = Vector(
            id=self.id,
            type=self.type,
            embedding=mergedEmbedding,
            createdAt=self.createdAt,
            updatedAt=datetime.now(timezone.utc),
        )
        mergedVector.EmitEvent(VectorsMergedEvent.FromModel(mergedVector, others))
        return mergedVector

    def UpdateEmbedding(self, newEmbedding: Tensor) -> None:
        """Update the vector's embedding."""
        if newEmbedding.ndim != 1:
            raise EmbeddingMustBeOneDimensionalException(newEmbedding.ndim)
        if not torch.isclose((newEmbedding / newEmbedding.norm()).norm(), torch.tensor(1.0)):
            raise EmbeddingMustBeNormalizedException((newEmbedding / newEmbedding.norm()).norm().item())
        if torch.equal(self.embedding, newEmbedding):
            return  # No change

        oldEmbedding = self.embedding.clone()

        self.embedding = newEmbedding
        self.updatedAt = datetime.now(timezone.utc)
        self.EmitEvent(VectorUpdatedEvent.FromModel(self, self.CalculateSimilarityToEmbedding(oldEmbedding)))

    def GetEmbeddingAsList(self) -> List[float]:
        """Get the embedding as a list of floats."""
        if self.IsOnCUDA():
            raise EmbeddingOnCUDANotSupportedException()
        return self.embedding.tolist()

    def MoveTensorToCPU(self) -> None:
        """Move the embedding tensor to CPU."""
        if self.IsOnCPU():
            return  # Already on CPU
        self.embedding = self.embedding.cpu()

    def MoveTensorToCUDA(self, device: Literal["cuda", "cuda:0", "cuda:1", "cuda:2", "cuda:3"] = "cuda") -> None:
        """Move the embedding tensor to CUDA device."""
        cudaDevice = torch.device(device)
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available on this system.")
        if self.IsOnCUDA() and self.embedding.device.index == cudaDevice.index:
            return  # Already on CUDA
        self.embedding = self.embedding.to(cudaDevice)

    def IsOnCPU(self) -> bool:
        """Check if the embedding tensor is on CPU."""
        return self.embedding.device.type == "cpu"

    def IsOnCUDA(self) -> bool:
        """Check if the embedding tensor is on CUDA."""
        return self.embedding.device.type == "cuda"
