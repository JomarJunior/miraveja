from typing import Callable
from sqlalchemy.orm import Session as DatabaseSession

from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.DatabaseManager.Infrastructure.Sql.Models import SqlDatabaseManager


class SqlDatabaseManagerFactory(IDatabaseManagerFactory):
    """
    Factory for creating SQL-based DatabaseManager instances.
    """

    def __init__(self, resourceFactory: Callable[[], DatabaseSession]) -> None:
        self._resourceFactory = resourceFactory

    def Create(
        self,
    ) -> SqlDatabaseManager:
        return SqlDatabaseManager(resourceFactory=self._resourceFactory)
