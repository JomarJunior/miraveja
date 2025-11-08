from datetime import datetime
from typing import Optional, Type

from pydantic import BaseModel, Field

from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class UpdateMemberIdentityByIdComand(BaseModel):
    memberId: MemberId = Field(..., description="The unique identifier of the member to update.")
    firstName: str = Field(..., min_length=1, max_length=50)
    lastName: str = Field(..., min_length=1, max_length=50)
    gender: Optional[str] = Field(default=None, max_length=20)
    dateOfBirth: Optional[datetime] = Field(default=None)


class UpdateMemberIdentityByIdHandler:
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

    async def Handle(self, command: UpdateMemberIdentityByIdComand) -> None:
        self._logger.Info(f"Updating member identity by ID with command: {command.model_dump_json(indent=4)}")

        with self._databaseManagerFactory.Create() as databaseManager:
            memberRepository: IMemberRepository = databaseManager.GetRepository(self._tMemberRepository)

            member = memberRepository.FindById(command.memberId)
            if not member:
                self._logger.Warning(f"Member with ID {command.memberId.id} not found.")
                return

            member.UpdateIdentity(
                firstName=command.firstName,
                lastName=command.lastName,
                gender=command.gender,
                dateOfBirth=command.dateOfBirth,
            )

            memberRepository.Save(member)
            databaseManager.Commit()
            self._logger.Info(f"Member with ID {command.memberId.id} updated successfully.")

        await self._eventDispatcher.DispatchAll(member.ReleaseEvents())
        self._logger.Info(f"Dispatched identity update events for member ID {command.memberId.id}.")
