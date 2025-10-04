from abc import ABC, abstractmethod
from types import TracebackType
from typing import Optional, Type, TypeVar

R = TypeVar("R")  # Repository Type


class IUnitOfWork(ABC):
    """Interface for Unit of Work pattern to manage atomic operations across repositories."""

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork":
        pass

    @abstractmethod
    def __exit__(
        self,
        excType: Optional[Type[BaseException]],
        excValue: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        pass

    @abstractmethod
    def Commit(self):
        pass

    @abstractmethod
    def Rollback(self):
        pass

    @abstractmethod
    def GetRepository(self, repositoryType: type[R]) -> R:
        pass


class IUnitOfWorkFactory(ABC):
    """Factory interface for creating Unit of Work instances."""

    @abstractmethod
    def Create(self) -> IUnitOfWork:
        pass
