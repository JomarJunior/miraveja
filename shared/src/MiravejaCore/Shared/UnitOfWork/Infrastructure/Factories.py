from typing import Callable
from sqlalchemy.orm import Session as DatabaseSession

from MiravejaCore.Shared.UnitOfWork.Domain.Interfaces import IUnitOfWorkFactory
from MiravejaCore.Shared.UnitOfWork.Infrastructure.Sql.Models import SqlUnitOfWork


class SqlUnitOfWorkFactory(IUnitOfWorkFactory):
    """
    Factory for creating SQL-based Unit of Work instances.
    """

    def __init__(self, resourceFactory: Callable[[], DatabaseSession]) -> None:
        self._resourceFactory = resourceFactory

    def Create(
        self,
    ) -> SqlUnitOfWork:
        return SqlUnitOfWork(resourceFactory=self._resourceFactory)
