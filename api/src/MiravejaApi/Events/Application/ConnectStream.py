from pydantic import BaseModel, Field, ValidationError
from fastapi import WebSocket, WebSocketDisconnect

from MiravejaCore.Shared.Events.Domain.Exceptions import DomainException, EventValidationError, InvalidJsonStringError
from MiravejaCore.Shared.Events.Domain.Events import MemberConnectedEvent
from MiravejaCore.Shared.Events.Domain.Services import EventFactory
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaApi.Connection.Domain.Models import WebSocketConnection, WebSocketConnectionManager


class ConnectStreamCommand(BaseModel):
    connection: WebSocket = Field(
        ..., description="The WebSocket connection to be managed"
    )  # * pydantic arbitrary type
    memberId: MemberId = Field(..., description="The ID of the member associated with the connection")

    model_config = {
        "arbitrary_types_allowed": True,  # * Allow arbitrary types
    }


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

        while True:
            try:
                event = await websocketConnection.ReceiveDomainEvent()
                await self.eventDispatcher.Dispatch(event)
            except WebSocketDisconnect:
                self.logger.Info(f"WebSocket disconnected for member ID: {command.memberId}")
                self.websocketConnectionManager.Disconnect(command.memberId)
                break
            except DomainException as de:
                self.logger.Error(f"Error in WebSocket connection for member ID {command.memberId}: {str(de)}")
                exceptionEvent = await self.eventFactory.CreateFromDomainException(exception=de)
                await self.eventDispatcher.Dispatch(exceptionEvent)
                await websocketConnection.SendDomainEvent(exceptionEvent)
            except ValidationError as ve:
                self.logger.Error(
                    f"Validation error in WebSocket connection for member ID {command.memberId}: {str(ve)}"
                )
                exception = EventValidationError(message=str(ve))
                exceptionEvent = await self.eventFactory.CreateFromDomainException(exception=exception)
                await self.eventDispatcher.Dispatch(exceptionEvent)
                await websocketConnection.SendDomainEvent(exceptionEvent)
                # Do not disconnect on exceptions other than WebSocketDisconnect
            except Exception as ex:
                self.logger.Error(
                    f"Unexpected error in WebSocket connection for member ID {command.memberId}: {str(ex)}"
                )
