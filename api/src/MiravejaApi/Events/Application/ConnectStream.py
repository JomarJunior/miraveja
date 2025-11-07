from pydantic import BaseModel, Field
from fastapi import WebSocket

from MiravejaCore.Shared.Events.Domain.Events import MemberConnectedEvent
from MiravejaCore.Shared.Events.Domain.Services import EventFactory
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaApi.Connection.Domain.Models import WebSocketConnection, WebSocketConnectionManager


class ConnectStreamCommand(BaseModel):
    connection: WebSocket = Field(..., description="The WebSocket connection to be managed")
    memberId: MemberId = Field(..., description="The ID of the member associated with the connection")


class ConnectStreamHandler:
    def __init__(
        self,
        websocketConnectionManager: WebSocketConnectionManager,
        eventFactory: EventFactory,
        logger: ILogger,
        eventDispatcher: EventDispatcher,
    ):
        self.websocketConnectionManager = websocketConnectionManager
        self.eventFactory = eventFactory
        self.logger = logger
        self.eventDispatcher = eventDispatcher

    async def Handle(self, command: ConnectStreamCommand):
        websocketConnection = WebSocketConnection(
            memberId=command.memberId,
            connection=command.connection,
            eventFactory=self.eventFactory,
        )
        await websocketConnection.Accept()
        self.websocketConnectionManager.Connect(websocketConnection)

        event: MemberConnectedEvent = MemberConnectedEvent.Create(  # type: ignore
            memberId=command.memberId,
            connectedAt=str(websocketConnection.openedAt),
        )
        await self.eventDispatcher.Dispatch(event)

        self.logger.Info(f"WebSocket connection established for member ID: {command.memberId}")

        try:
            while True:
                event = await websocketConnection.ReceiveDomainEvent()
                await self.eventDispatcher.Dispatch(event)
        except Exception as e:
            self.logger.Error(f"Error in WebSocket connection for member ID {command.memberId}: {str(e)}")
        finally:
            self.websocketConnectionManager.Disconnect(command.memberId)
            await websocketConnection.Close()
            self.logger.Info(f"WebSocket connection closed for member ID: {command.memberId}")
