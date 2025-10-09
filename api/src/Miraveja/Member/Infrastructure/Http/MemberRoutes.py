from typing import Optional
from fastapi import APIRouter, Depends

from Miraveja.Member.Application.ListAllMembers import ListAllMembersCommand
from Miraveja.Member.Application.RegisterMember import RegisterMemberCommand
from Miraveja.Member.Infrastructure.Http.MemberController import FindMemberByIdCommand, MemberController
from Miraveja.Shared.Identifiers.Models import MemberId
from Miraveja.Shared.Keycloak.Domain.Models import KeycloakUser
from Miraveja.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider
from Miraveja.Shared.Utils.Types.Handler import HandlerResponse

BASE_ROUTE = "/members"


class MemberRoutes:
    @staticmethod
    def RegisterRoutes(
        router: APIRouter, controller: MemberController, keycloakDependencyProvider: KeycloakDependencyProvider
    ):
        @router.get(f"{BASE_ROUTE}/", response_model=HandlerResponse)
        async def ListAllMembersRoute(command: Optional[ListAllMembersCommand] = None):
            return controller.ListAllMembers(command)

        @router.get(f"{BASE_ROUTE}/{{memberId}}", response_model=HandlerResponse)
        async def FindMemberByIdRoute(memberId: str):
            command = FindMemberByIdCommand(memberId=MemberId(id=memberId))
            return controller.FindMemberById(command)

        @router.post(f"{BASE_ROUTE}/", response_model=HandlerResponse)
        async def RegisterMemberRoute(
            command: RegisterMemberCommand,
            agent: KeycloakUser = Depends(keycloakDependencyProvider.RequireAdminPrivileges()),  # type: ignore
        ):
            return controller.RegisterMember(command, agent)
