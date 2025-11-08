from typing import Any, Callable, Dict, Optional, Type

from sqlalchemy.orm import Session as DatabaseSession

from MiravejaCore.Shared.DatabaseManager.Domain.Exceptions import SessionNotInitializedError
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManager


class SqlDatabaseManager(IDatabaseManager):
    def __init__(self, resourceFactory: Callable[[], DatabaseSession]) -> None:
        self._resourceFactory = resourceFactory
        self._session: Optional[DatabaseSession] = None
        self._repositories: Dict[Type[Any], Any] = {}

    def __enter__(self) -> "SqlDatabaseManager":
        self._session = self._resourceFactory()
        self._repositories = {}
        return self

    def __exit__(
        self, excType: Optional[Type[BaseException]], excValue: Optional[BaseException], traceback: Optional[Any]
    ) -> Optional[bool]:
        if excType is not None:
            self.Rollback()
        if self._session:
            self._session.close()

    def Commit(self) -> None:
        if self._session:
            self._session.commit()

    def Rollback(self) -> None:
        if self._session:
            self._session.rollback()

    def GetRepository(self, repositoryType: Type[Any]) -> Any:
        if repositoryType not in self._repositories:
            if self._session is None:
                raise SessionNotInitializedError()
            # Here is the difference from a generic implementation:
            # The same DatabaseSession is passed to all repositories, ensuring they share the same transaction context.
            self._repositories[repositoryType] = repositoryType(self._session)
        return self._repositories[repositoryType]
