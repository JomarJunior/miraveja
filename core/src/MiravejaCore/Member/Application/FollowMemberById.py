from typing import Type

from pydantic import BaseModel, Field

from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class FollowMemberByIdCommand(BaseModel):
    memberIdToFollow: MemberId = Field(..., description="The unique identifier of the member to follow.")
    agentId: MemberId = Field(..., description="The unique identifier of the member who is following.")


class FollowMemberByIdHandler:
    def __init__(
        self,
        databaseManagerFactory: IDatabaseManagerFactory,
        tMemberRepository: Type[IMemberRepository],
        logger: ILogger,
        eventDispatcher: EventDispatcher,
    ):
        self._databaseManagerFactory = databaseManagerFactory
        self._tMemberRepository = tMemberRepository
        self._logger = logger
        self._eventDispatcher = eventDispatcher

    async def Handle(self, command: FollowMemberByIdCommand) -> None:
        self._logger.Info(f"Following member by ID with command: {command.model_dump_json(indent=4)}")

        with self._databaseManagerFactory.Create() as databaseManager:
            memberRepository: IMemberRepository = databaseManager.GetRepository(self._tMemberRepository)

            agent = memberRepository.FindById(command.agentId)
            if not agent:
                self._logger.Warning(f"Agent member with ID {command.agentId.id} not found.")
                return

            memberToFollow = memberRepository.FindById(command.memberIdToFollow)
            if not memberToFollow:
                self._logger.Warning(f"Member to follow with ID {command.memberIdToFollow.id} not found.")
                return

            agent.FollowMember(memberToFollow.id)
            memberRepository.Save(agent)
            databaseManager.Commit()
            self._logger.Info(
                f"Member with ID {command.agentId.id} is now following member ID {command.memberIdToFollow.id}."
            )

        await self._eventDispatcher.DispatchAll(agent.ReleaseEvents())
        self._logger.Info(f"Dispatched follow events for member ID {command.agentId.id}.")
