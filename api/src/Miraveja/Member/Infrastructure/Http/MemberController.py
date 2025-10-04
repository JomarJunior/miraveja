from typing import Optional

from fastapi import HTTPException
from Miraveja.Member.Application.FindMemberById import FindMemberByIdCommand, FindMemberByIdHandler
from Miraveja.Member.Application.ListAllMembers import ListAllMembersCommand, ListAllMembersHandler
from Miraveja.Member.Application.RegisterMember import RegisterMemberCommand, RegisterMemberHandler
from Miraveja.Shared.Errors.Models import DomainException
from Miraveja.Shared.Keycloak.Domain.Models import KeycloakUser
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.Utils.Types.Handler import HandlerResponse


class MemberController:
    def __init__(
        self,
        listAllMembersHandler: ListAllMembersHandler,
        findMemberByIdHandler: FindMemberByIdHandler,
        registerMemberHandler: RegisterMemberHandler,
        logger: ILogger,
    ):
        self._listAllMembersHandler = listAllMembersHandler
        self._findMemberByIdHandler = findMemberByIdHandler
        self._registerMemberHandler = registerMemberHandler
        self._logger = logger

    def ListAllMembers(self, command: Optional[ListAllMembersCommand] = None) -> HandlerResponse:
        try:
            if command is None:
                command = ListAllMembersCommand()
            return self._listAllMembersHandler.Handle(command)
        except DomainException as domainException:
            self._logger.Error(f"{str(domainException)}")
            raise HTTPException(status_code=400, detail=str(domainException)) from domainException
        except Exception as exception:
            self._logger.Error(f"Unexpected error during listing members: {str(exception)}")
            raise HTTPException(status_code=500, detail="Internal server error") from exception

    def FindMemberById(self, command: FindMemberByIdCommand) -> HandlerResponse:
        try:
            member: Optional[HandlerResponse] = self._findMemberByIdHandler.Handle(command)
        except DomainException as domainException:
            self._logger.Error(f"{str(domainException)}")
            raise HTTPException(status_code=400, detail=str(domainException)) from domainException

        except Exception as exception:
            self._logger.Error(f"Unexpected error during finding member by ID: {str(exception)}")
            raise HTTPException(status_code=500, detail="Internal server error") from exception

        if member is None:
            raise HTTPException(status_code=404, detail="Member not found")
        return member

    def RegisterMember(self, command: RegisterMemberCommand, agent: KeycloakUser) -> HandlerResponse:
        try:
            self._registerMemberHandler.Handle(command)
            self._logger.Info(f"Member registered successfully: {command.id}")
            self._logger.Info(f"Registered by agent: {agent.id}")
            return {"message": "Member registered successfully"}

        except DomainException as domainException:
            self._logger.Error(f"{str(domainException)}")
            raise HTTPException(status_code=400, detail=str(domainException)) from domainException

        except Exception as exception:
            self._logger.Error(f"Unexpected error during member registration: {str(exception)}")
            raise HTTPException(status_code=500, detail="Internal server error") from exception
