from typing import Type
from Miraveja.Member.Domain.Interfaces import IMemberRepository
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.UnitOfWork.Domain.Interfaces import IUnitOfWorkFactory
from Miraveja.Shared.Utils.Repository.Queries import ListAllQuery
from Miraveja.Shared.Utils.Types.Handler import HandlerResponse


class ListAllMembersCommand(ListAllQuery):
    pass


class ListAllMembersHandler:
    def __init__(
        self, databaseUOWFactory: IUnitOfWorkFactory, tMemberRepository: Type[IMemberRepository], logger: ILogger
    ):
        self._databaseUOWFactory = databaseUOWFactory
        self._tMemberRepository = tMemberRepository
        self._logger = logger

    def Handle(self, command: ListAllMembersCommand) -> HandlerResponse:
        self._logger.Info(f"Listing all members with command: {command.model_dump_json(indent=4)}")
        with self._databaseUOWFactory.Create() as unitOfWork:
            repository: IMemberRepository = unitOfWork.GetRepository(self._tMemberRepository)
            allMembers = repository.ListAll(command)
            totalMembers = repository.Count()

            members = list(map(lambda member: member.model_dump(), allMembers))
            return {
                "items": members,
                "pagination": {
                    "total": totalMembers,
                    "offset": command.offset if hasattr(command, "offset") else 0,
                    "limit": command.limit if hasattr(command, "limit") else len(members),
                },
            }
