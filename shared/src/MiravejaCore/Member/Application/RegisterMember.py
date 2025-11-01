from typing import Type

from pydantic import BaseModel, EmailStr, Field

from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Member.Domain.Models import Member
from MiravejaCore.Member.Domain.Exceptions import MemberAlreadyExistsException
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory


class RegisterMemberCommand(BaseModel):
    id: str = Field(..., description="Unique identifier for the member")
    email: EmailStr = Field(..., description="Email address of the member")
    firstName: str = Field(..., min_length=1, max_length=50, description="First name of the member")
    lastName: str = Field(..., min_length=1, max_length=50, description="Last name of the member")
    # Aditional fields can be added here if needed


class RegisterMemberHandler:
    def __init__(
        self,
        databaseUOWFactory: IDatabaseManagerFactory,
        tMemberRepository: Type[IMemberRepository],
        logger: ILogger,
    ):
        self._databaseUOWFactory = databaseUOWFactory
        self._tMemberRepository = tMemberRepository
        self._logger = logger

    def Handle(self, command: RegisterMemberCommand) -> None:
        self._logger.Info(f"Registering member with command: {command.model_dump_json(indent=4)}")
        memberId: MemberId = MemberId(id=command.id)

        self._logger.Debug(f"Creating member entity with ID: {memberId.id}")
        member = Member.Register(
            id=memberId,
            email=command.email,
            firstName=command.firstName,
            lastName=command.lastName,
        )
        self._logger.Debug(f"Created member entity: {member.model_dump_json(indent=4)}")

        with self._databaseUOWFactory.Create() as databaseManager:

            if databaseManager.GetRepository(self._tMemberRepository).MemberExists(memberId):
                self._logger.Error(f"Member with ID {memberId.id} already exists.")
                raise MemberAlreadyExistsException(memberId.id)

            databaseManager.GetRepository(self._tMemberRepository).Save(member)
            databaseManager.Commit()

        self._logger.Info(f"Member registered successfully: {member.model_dump_json(indent=4)}")
