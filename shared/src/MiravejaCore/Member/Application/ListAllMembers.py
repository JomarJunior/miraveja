from typing import Type
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.Utils.Repository.Queries import ListAllQuery
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse


class ListAllMembersCommand(ListAllQuery):
    pass


class ListAllMembersHandler:
    def __init__(
        self,
        databaseManagerFactory: IDatabaseManagerFactory,
        tMemberRepository: Type[IMemberRepository],
        logger: ILogger,
    ):
        self._databaseManagerFactory = databaseManagerFactory
        self._tMemberRepository = tMemberRepository
        self._logger = logger

    def Handle(self, command: ListAllMembersCommand) -> HandlerResponse:
        self._logger.Info(f"Listing all members with command: {command.model_dump_json(indent=4)}")
        with self._databaseManagerFactory.Create() as databaseManager:
            repository: IMemberRepository = databaseManager.GetRepository(self._tMemberRepository)
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
