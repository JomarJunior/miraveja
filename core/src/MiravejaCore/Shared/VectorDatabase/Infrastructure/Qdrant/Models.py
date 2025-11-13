from typing import Any, Callable, Dict, Optional, Type

from qdrant_client import QdrantClient

from MiravejaCore.Shared.VectorDatabase.Domain.Configuration import QdrantConfig
from MiravejaCore.Shared.VectorDatabase.Domain.Exceptions import ClientNotInitializedError
from MiravejaCore.Shared.VectorDatabase.Domain.Interfaces import IVectorDatabaseManager
from MiravejaCore.Vector.Application.GenerateTextVector import VectorType


class QdrantVectorDatabaseManager(IVectorDatabaseManager):
    """
    Qdrant implementation of the vector database manager.
    Manages the lifecycle and operations of the Qdrant vector database.
    """

    def __init__(self, resourceFactory: Callable[[], QdrantClient], config: QdrantConfig):
        """
        Initializes the QdrantVectorDatabaseManager with a resource factory.

        Args:
            resourceFactory (Callable[[], QdrantClient]):
            A factory function that creates and returns a QdrantClient instance.
        """
        self._resourceFactory = resourceFactory
        self.client: Optional[QdrantClient] = None
        self._config = config
        self._repositories: Dict[Type[Any], Any] = {}

    def __enter__(self) -> "QdrantVectorDatabaseManager":
        """
        Enters the context manager, initializing the Qdrant client.
        Repositories are cleared to ensure a fresh state.
        """
        self.client = self._resourceFactory()
        self._repositories.clear()

        return self

    def __exit__(
        self,
        excType: Optional[Type[BaseException]],
        excValue: Optional[BaseException],
        traceback: Optional[Any],
    ) -> None:
        """
        Exits the context manager, closing the Qdrant client.
        """
        if self.client:
            self.client.close()
            self.client = None
        self._repositories.clear()

    def GetClient(self) -> QdrantClient:
        """
        Retrieves the Qdrant client instance.

        Returns:
            QdrantClient: The Qdrant client instance.

        Raises:
            ValueError: If the client is not initialized.
        """
        if self.client is None:
            raise ClientNotInitializedError()
        return self.client

    def GetRepository(self, repositoryType: Type[Any]) -> Any:
        """
        Retrieves a repository of the specified type.

        Args:
            repositoryType (Type[Any]): The type of the repository to retrieve.

        Returns:
            Any: An instance of the requested repository type.
        """
        if repositoryType not in self._repositories:
            if self.client is None:
                raise ClientNotInitializedError()
            # Pass the same client instance to all repositories
            self._repositories[repositoryType] = repositoryType(self.client, self._config)
        return self._repositories[repositoryType]
