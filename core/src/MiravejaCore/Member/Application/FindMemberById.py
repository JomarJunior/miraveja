from typing import Optional, Type
from pydantic import BaseModel, Field

from MiravejaCore.Member.Domain.Exceptions import MemberNotFoundException
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse


class FindMemberByIdCommand(BaseModel):
    memberId: MemberId = Field(..., description="The unique identifier of the member to find.")


class FindMemberByIdHandler:
    def __init__(
        self,
        databaseManagerFactory: IDatabaseManagerFactory,
        tMemberRepository: Type[IMemberRepository],
        logger: ILogger,
    ):
        self._databaseManagerFactory = databaseManagerFactory
        self._tMemberRepository = tMemberRepository
        self._logger = logger

    def Handle(self, command: FindMemberByIdCommand) -> Optional[HandlerResponse]:
        self._logger.Info(f"Finding member by ID with command: {command.model_dump_json(indent=4)}")

        with self._databaseManagerFactory.Create() as databaseManager:
            member = databaseManager.GetRepository(self._tMemberRepository).FindById(command.memberId)
        if not member:
            self._logger.Warning(f"Member with ID {command.memberId.id} not found.")
            raise MemberNotFoundException(command.memberId.id)

        self._logger.Info(f"Member with ID {command.memberId.id} found: {member.model_dump_json(indent=4)}")
        return member.model_dump()
