from typing import Optional
from fastapi import APIRouter, Depends

from MiravejaCore.Member.Application.ListAllMembers import ListAllMembersCommand
from MiravejaCore.Member.Application.RegisterMember import RegisterMemberCommand
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse
from MiravejaApi.Member.Infrastructure.Http.MemberController import FindMemberByIdCommand, MemberController

BASE_ROUTE = "/members"


class MemberRoutes:
    @staticmethod
    def RegisterRoutes(
        router: APIRouter, controller: MemberController, keycloakDependencyProvider: KeycloakDependencyProvider
    ):
        @router.get(f"{BASE_ROUTE}/", response_model=HandlerResponse)
        async def ListAllMembersRoute(command: Optional[ListAllMembersCommand] = None):
            return await controller.ListAllMembers(command)

        @router.get(f"{BASE_ROUTE}/{{memberId}}", response_model=HandlerResponse)
        async def FindMemberByIdRoute(memberId: str):
            command = FindMemberByIdCommand(memberId=MemberId(id=memberId))
            return await controller.FindMemberById(command)

        @router.post(f"{BASE_ROUTE}/", response_model=HandlerResponse)
        async def RegisterMemberRoute(
            command: RegisterMemberCommand,
            agent: KeycloakUser = Depends(keycloakDependencyProvider.RequireAdminPrivileges()),  # type: ignore
        ):
            return await controller.RegisterMember(command, agent)
