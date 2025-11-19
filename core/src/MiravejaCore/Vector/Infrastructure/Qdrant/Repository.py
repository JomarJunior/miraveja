from typing import List

from qdrant_client import QdrantClient
from qdrant_client.http.models import ScoredPoint
from torch import Tensor

from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Shared.VectorDatabase.Domain.Configuration import QdrantConfig
from MiravejaCore.Vector.Domain.Enums import VectorType
from MiravejaCore.Vector.Domain.Exceptions import VectorNotFoundException
from MiravejaCore.Vector.Domain.Interfaces import IVectorRepository
from MiravejaCore.Vector.Domain.Models import Vector
from MiravejaCore.Vector.Infrastructure.Qdrant.Entities import QdrantPoint


class QdrantVectorRepository(IVectorRepository):
    """Qdrant Vector Repository implementation."""

    def __init__(
        self,
        client: QdrantClient,
        config: QdrantConfig,
    ):
        self._client = client
        self._config = config
        self._collectionName = config.collectionName

    async def FindById(self, vectorId: VectorId) -> Vector:
        """Find a vector by its ID."""
        # Try to find in IMAGE collection first
        results = self._client.retrieve(
            collection_name=self._config.GetFullCollectionName(vectorType=VectorType.IMAGE),
            ids=[str(vectorId)],
            with_vectors=True,
        )

        if not results:
            # Fallback to TEXT collection
            results = self._client.retrieve(
                collection_name=self._config.GetFullCollectionName(vectorType=VectorType.TEXT),
                ids=[str(vectorId)],
            )

        if not results:
            raise VectorNotFoundException(vectorId=str(vectorId))

        point: QdrantPoint = QdrantPoint.FromQdrantResponse(results[0])
        return Vector.model_validate(point.model_dump())

    async def FindManyByIds(self, vectorIds: List[VectorId]) -> List[Vector]:
        """Find many vectors by their IDs."""
        strIds = [str(vectorId) for vectorId in vectorIds]
        # Try to find in IMAGE collection first
        results = self._client.retrieve(
            collection_name=self._config.GetFullCollectionName(VectorType.IMAGE),
            with_vectors=True,
            ids=strIds,
        )

        if len(results) != len(strIds):
            # Fallback to TEXT collection for missing IDs
            results.extend(
                self._client.retrieve(
                    collection_name=self._config.GetFullCollectionName(VectorType.TEXT),
                    ids=[id for id in strIds if id not in [str(point.id) for point in results]],
                )
            )

        foundVectors = []
        for result in results:
            point: QdrantPoint = QdrantPoint.FromQdrantResponse(result)
            foundVectors.append(Vector.model_validate(point.model_dump()))

        return foundVectors

    async def Save(self, vector) -> None:
        """Save a vector to the repository."""
        point = QdrantPoint.FromDomain(vector)
        self._client.upsert(
            collection_name=self._config.GetFullCollectionName(vector.type),
            points=[point.ToPointStruct()],
        )

    async def SearchSimilar(self, embedding: Tensor, topK: int, vectorType: VectorType | None = None) -> List[Vector]:
        """Search for similar vectors."""
        embeddingList = embedding.tolist()
        collectionsToSearch = []
        if vectorType:
            # Search only in the specified vector type collection
            collectionsToSearch.append(self._config.GetFullCollectionName(vectorType))
        else:
            # Search in both IMAGE and TEXT collections
            collectionsToSearch.append(self._config.GetFullCollectionName(VectorType.IMAGE))
            collectionsToSearch.append(self._config.GetFullCollectionName(VectorType.TEXT))

        results: List[ScoredPoint] = []
        for collection in collectionsToSearch:
            searchResults = self._client.query_points(
                collection_name=collection,
                query=embeddingList,
                limit=topK,
                with_vectors=True,
            )
            results.extend(searchResults.points)

        similarVectors = []
        for result in results:
            point: QdrantPoint = QdrantPoint.FromQdrantResponse(result)
            similarVectors.append(Vector.model_validate(point.model_dump()))

        return similarVectors

    async def TotalCount(self, vectorType: VectorType | None = None) -> int:
        """Get the total count of vectors in the repository."""
        raise NotImplementedError("TotalCount method is not implemented yet.")

    async def FindByType(self, vectorType: VectorType) -> List[Vector]:
        """Find vectors by their type."""
        raise NotImplementedError("FindByType method is not implemented yet.")
