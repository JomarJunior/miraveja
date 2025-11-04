from datetime import datetime
from typing import Optional, Type

from pydantic import BaseModel, EmailStr, Field

from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Member.Domain.Models import Member
from MiravejaCore.Member.Domain.Exceptions import MemberAlreadyExistsException
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId, MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory


class RegisterMemberCommand(BaseModel):
    # We do not generate an ID for a member; the id is provided externally (e.g., by Keycloak)
    id: str = Field(..., description="Unique identifier for the member")
    email: EmailStr = Field(..., description="Email address of the member")
    username: str = Field(..., min_length=3, max_length=41, description="Username of the member")
    bio: str = Field("", max_length=500, description="Short biography of the member")
    avatarId: Optional[int] = Field(None, description="Avatar image ID of the member")
    coverId: Optional[int] = Field(None, description="Cover image ID of the member")
    firstName: str = Field(..., min_length=1, max_length=50, description="First name of the member")
    lastName: str = Field(..., min_length=1, max_length=50, description="Last name of the member")
    gender: Optional[str] = Field(None, max_length=50, description="Gender of the member")
    dateOfBirth: Optional[str] = Field(None, description="Date of birth of the member, in ISO 8601 format")
    # Aditional fields can be added here if needed


class RegisterMemberHandler:
    def __init__(
        self,
        databaseManagerFactory: IDatabaseManagerFactory,
        tMemberRepository: Type[IMemberRepository],
        eventDispatcher: EventDispatcher,
        logger: ILogger,
    ):
        self._databaseManagerFactory = databaseManagerFactory
        self._tMemberRepository = tMemberRepository
        self._eventDispatcher = eventDispatcher
        self._logger = logger

    async def Handle(self, command: RegisterMemberCommand) -> None:
        self._logger.Info(f"Registering member with command: {command.model_dump_json(indent=4)}")
        memberId: MemberId = MemberId(id=command.id)

        self._logger.Debug(f"Creating member entity with ID: {memberId.id}")
        member = Member.Register(
            id=memberId,
            email=command.email,
            username=command.username,
            bio=command.bio,
            avatarId=ImageMetadataId(id=command.avatarId) if command.avatarId is not None else None,
            coverId=ImageMetadataId(id=command.coverId) if command.coverId is not None else None,
            firstName=command.firstName,
            lastName=command.lastName,
            gender=command.gender,
            dateOfBirth=datetime.fromisoformat(command.dateOfBirth) if command.dateOfBirth else None,
        )
        self._logger.Debug(f"Created member entity: {member.model_dump_json(indent=4)}")

        with self._databaseManagerFactory.Create() as databaseManager:
            memberRepository: IMemberRepository = databaseManager.GetRepository(self._tMemberRepository)

            if memberRepository.MemberExists(memberId):
                self._logger.Error(f"Member with ID {memberId.id} already exists.")
                raise MemberAlreadyExistsException(memberId.id)

            memberRepository.Save(member)

            databaseManager.Commit()

        await self._eventDispatcher.DispatchAll(member.ReleaseEvents())

        self._logger.Info(f"Member registered successfully: {member.model_dump_json(indent=4)}")
