from abc import ABC, abstractmethod
from typing import List, Optional

from PIL import Image
from torch import Tensor

from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Vector.Domain.Enums import VectorType
from MiravejaCore.Vector.Domain.Models import Vector


class IVectorRepository(ABC):
    """Interface for vector databases repositories."""

    @abstractmethod
    async def Save(self, vector) -> None:
        """Save a vector to the repository."""

    @abstractmethod
    async def FindById(self, vectorId: VectorId) -> Vector:
        """Find a vector by its ID."""

    @abstractmethod
    async def FindManyByIds(self, vectorIds: List[VectorId]) -> List[Vector]:
        """Find multiple vectors by their IDs. Must preserve the order of the input IDs."""

    @abstractmethod
    async def FindByType(self, vectorType: VectorType) -> List[Vector]:
        """Find vectors by their type."""

    @abstractmethod
    async def SearchSimilar(
        self,
        embedding: Tensor,
        topK: int,
        vectorType: Optional[VectorType] = None,
    ) -> List[Vector]:
        """Search for the most similar vectors to the given embedding."""

    @abstractmethod
    async def TotalCount(self, vectorType: Optional[VectorType] = None) -> int:
        """Get the total count of vectors, optionally filtered by type."""


class IEmbeddingProvider(ABC):
    """Interface for embedding providers."""

    @abstractmethod
    async def GenerateImageEmbedding(self, image: Image.Image) -> Tensor:
        """Generate an embedding for the given image data."""

    @abstractmethod
    async def GenerateTextEmbedding(self, text: str) -> Tensor:
        """Generate an embedding for the given text."""
