from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type, TypeVar

from qdrant_client import QdrantClient

R = TypeVar("R")  # Repository Type


class IVectorDatabaseManager(ABC):
    """Interface for managing Qdrant vector database operations."""

    @abstractmethod
    def __enter__(self) -> "IVectorDatabaseManager":
        """Enter the context manager and establish connection."""

    @abstractmethod
    def __exit__(
        self,
        excType: Optional[Type[BaseException]],
        excValue: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Exit the context manager and cleanup resources."""

    @abstractmethod
    def GetRepository(self, repositoryType: type[R]) -> R:
        """
        Get or create a repository instance.

        Args:
            repositoryType: The repository class type to instantiate

        Returns:
            An instance of the requested repository type
        """

    @abstractmethod
    def GetClient(self) -> QdrantClient:
        """
        Get the underlying Qdrant client.

        Returns:
            The active QdrantClient instance
        """


class IVectorDatabaseManagerFactory(ABC):
    """Factory interface for creating VectorDatabaseManager instances."""

    @abstractmethod
    def Create(self) -> IVectorDatabaseManager:
        """
        Create a new VectorDatabaseManager instance.

        Returns:
            A new IVectorDatabaseManager instance
        """
