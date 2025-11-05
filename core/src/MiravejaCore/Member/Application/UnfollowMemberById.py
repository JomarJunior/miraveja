from typing import Type
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from pydantic import BaseModel, Field


class UnfollowMemberByIdCommand(BaseModel):
    memberIdToUnfollow: MemberId = Field(..., description="The unique identifier of the member to unfollow.")
    agentId: MemberId = Field(..., description="The unique identifier of the member who is unfollowing.")


class UnfollowMemberByIdHandler:
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

    async def Handle(self, command: UnfollowMemberByIdCommand) -> None:
        self._logger.Info(f"Unfollowing member by ID with command: {command.model_dump_json(indent=4)}")

        with self._databaseManagerFactory.Create() as databaseManager:
            memberRepository: IMemberRepository = databaseManager.GetRepository(self._tMemberRepository)

            agent = memberRepository.FindById(command.agentId)
            if not agent:
                self._logger.Warning(f"Agent member with ID {command.agentId.id} not found.")
                return

            memberToUnfollow = memberRepository.FindById(command.memberIdToUnfollow)
            if not memberToUnfollow:
                self._logger.Warning(f"Member to unfollow with ID {command.memberIdToUnfollow.id} not found.")
                return

            agent.UnfollowMember(memberToUnfollow.id)
            memberRepository.Save(agent)
            databaseManager.Commit()
            self._logger.Info(
                f"Member with ID {command.agentId.id} has unfollowed member ID {command.memberIdToUnfollow.id}."
            )

        await self._eventDispatcher.DispatchAll(agent.ReleaseEvents())
        self._logger.Info(f"Dispatched unfollow events for member ID {command.agentId.id}.")
