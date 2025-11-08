from typing import Optional, Type

from pydantic import BaseModel, Field

from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId, MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class UpdateMemberProfileByIdCommand(BaseModel):
    memberId: MemberId = Field(..., description="The unique identifier of the member to update.")
    bio: str = Field(default="", max_length=500)
    avatarId: Optional[ImageMetadataId] = Field(default=None)
    coverId: Optional[ImageMetadataId] = Field(default=None)


class UpdateMemberProfileByIdHandler:
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

    async def Handle(self, command: UpdateMemberProfileByIdCommand) -> None:
        self._logger.Info(f"Updating member profile by ID with command: {command.model_dump_json(indent=4)}")

        with self._databaseManagerFactory.Create() as databaseManager:
            memberRepository: IMemberRepository = databaseManager.GetRepository(self._tMemberRepository)

            member = memberRepository.FindById(command.memberId)
            if not member:
                self._logger.Warning(f"Member with ID {command.memberId.id} not found.")
                return

            member.UpdateProfile(bio=command.bio, avatarId=command.avatarId, coverId=command.coverId)
            memberRepository.Save(member)
            databaseManager.Commit()
            self._logger.Info(f"Member with ID {command.memberId.id} profile has been updated.")

        await self._eventDispatcher.DispatchAll(member.ReleaseEvents())
        self._logger.Info(f"Dispatched profile update events for member ID {command.memberId.id}.")
