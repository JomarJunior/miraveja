from fastapi import APIRouter, Depends
from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse
from MiravejaCore.Vector.Application.SearchVectorsByText import SearchVectorsByTextCommand

from MiravejaApi.Vector.Infrastructure.Http.VectorController import VectorController

BASE_ROUTE = "/vectors"


class VectorRoutes:
    @staticmethod
    def RegisterRoutes(
        router: APIRouter, controller: VectorController, keycloakDependencyProvider: KeycloakDependencyProvider
    ):
        @router.get(f"{BASE_ROUTE}/search-by-text", response_model=HandlerResponse)
        async def SearchVectorsByTextRoute(
            command: SearchVectorsByTextCommand,
            agent: KeycloakUser = Depends(keycloakDependencyProvider.RequireAuthentication),  # pylint: disable=W0613
        ):
            return await controller.SearchVectorsByText(command)

        @router.get(f"{BASE_ROUTE}/{{vectorId}}", response_model=HandlerResponse)
        async def FindVectorByIdRoute(
            vectorId: str,
            agent: KeycloakUser = Depends(keycloakDependencyProvider.RequireAuthentication),  # pylint: disable=W0613
        ):
            return await controller.FindVectorById(VectorId(id=vectorId))
