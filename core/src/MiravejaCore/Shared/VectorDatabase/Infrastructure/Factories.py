from typing import Callable

from qdrant_client import QdrantClient

from MiravejaCore.Shared.VectorDatabase.Domain.Configuration import QdrantConfig
from MiravejaCore.Shared.VectorDatabase.Domain.Interfaces import IVectorDatabaseManager, IVectorDatabaseManagerFactory
from MiravejaCore.Shared.VectorDatabase.Infrastructure.Qdrant.Models import (
    QdrantVectorDatabaseManager,
)


class QdrantVectorDatabaseManagerFactory(IVectorDatabaseManagerFactory):
    """
    Factory for creating Qdrant vector database manager instances.
    """

    def __init__(self, resourceFactory: Callable[[], QdrantClient], config: QdrantConfig):
        """
        Initializes the factory with a resource factory.

        Args:
            resourceFactory (Callable[[], QdrantClient]):
            A factory function that creates and returns a QdrantClient instance.
        """
        self._resourceFactory = resourceFactory
        self._config = config

    def Create(self) -> IVectorDatabaseManager:
        """
        Creates a new instance of QdrantVectorDatabaseManager.

        Returns:
            IVectorDatabaseManager: A new Qdrant vector database manager instance.
        """
        return QdrantVectorDatabaseManager(self._resourceFactory, self._config)
