from typing import Type

from pydantic import BaseModel, Field

from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class AddFriendByIdCommand(BaseModel):
    friendId: MemberId = Field(..., description="The unique identifier of the member to add as a friend.")
    agentId: MemberId = Field(..., description="The unique identifier of the member who is adding the friend.")


class AddFriendByIdHandler:
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

    async def Handle(self, command: AddFriendByIdCommand) -> None:
        self._logger.Info(f"Adding friend by ID with command: {command.model_dump_json(indent=4)}")

        with self._databaseManagerFactory.Create() as databaseManager:
            memberRepository: IMemberRepository = databaseManager.GetRepository(self._tMemberRepository)

            agent = memberRepository.FindById(command.agentId)
            if not agent:
                self._logger.Warning(f"Agent member with ID {command.agentId.id} not found.")
                return

            friend = memberRepository.FindById(command.friendId)
            if not friend:
                self._logger.Warning(f"Friend member with ID {command.friendId.id} not found.")
                return

            agent.AddFriend(friend.id)
            memberRepository.Save(agent)
            databaseManager.Commit()
            self._logger.Info(
                f"Member with ID {command.friendId.id} has been added as a friend to member ID {command.agentId.id}."
            )

        await self._eventDispatcher.DispatchAll(agent.ReleaseEvents())
        self._logger.Info(f"Dispatched friend addition events for member ID {command.agentId.id}.")
