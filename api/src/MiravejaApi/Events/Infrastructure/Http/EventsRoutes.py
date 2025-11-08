from typing import Annotated, Optional
from fastapi import APIRouter, Depends, WebSocket, Query
from MiravejaCore.Member.Domain.Interfaces import MemberId
from MiravejaCore.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaApi.Events.Application.ConnectStream import ConnectStreamCommand
from MiravejaApi.Events.Infrastructure.Http.EventsController import EventsController

BASE_ROUTE = "/events"


class EventsRoutes:
    @staticmethod
    def RegisterRoutes(
        router: APIRouter, controller: EventsController, keycloakDependencyProvider: KeycloakDependencyProvider
    ):
        @router.websocket(f"/ws{BASE_ROUTE}")
        async def ConnectStreamRoute(
            websocket: WebSocket,
            topics: Annotated[Optional[str], Query()] = None,
            agent: KeycloakUser = Depends(keycloakDependencyProvider.RequireAuthenticationWebSocket),
        ):
            command = ConnectStreamCommand(
                connection=websocket, memberId=MemberId(id=agent.id), topics=topics.split(",") if topics else []
            )
            return await controller.ConnectStream(command)
