import asyncio
from typing import List, Type
from pydantic import BaseModel, Field, ValidationError
from fastapi import WebSocket, WebSocketDisconnect

from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent, IEventConsumer, IEventSubscriber
from MiravejaCore.Shared.Events.Domain.Exceptions import DomainException, EventValidationError
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


class WebSocketEventSubscriber(IEventSubscriber[DomainEvent]):
    def __init__(self, websocketConnection: WebSocketConnection, logger: ILogger):
        self.websocketConnection = websocketConnection
        self.logger = logger

    async def Handle(self, event: DomainEvent) -> None:
        try:
            if event.aggregateId == str(self.websocketConnection.memberId):
                return  # Ignore events not meant for this connection
            await self.websocketConnection.SendDomainEvent(event)
        except WebSocketDisconnect:
            self.logger.Info(f"WebSocket disconnected for member ID: {self.websocketConnection.memberId}")
            # Connection will be removed by the main handler loop
        except Exception as ex:
            self.logger.Error(
                (
                    "Unexpected error sending event "
                    f"to WebSocket for member ID {self.websocketConnection.memberId}: {str(ex)}"
                )
            )


class ConnectStreamHandler:
    def __init__(
        self,
        websocketConnectionManager: WebSocketConnectionManager,
        eventFactory: EventFactory,
        eventConsumer: IEventConsumer,
        logger: ILogger,
        eventDispatcher: EventDispatcher,
    ):
        self.websocketConnectionManager = websocketConnectionManager
        self.eventFactory = eventFactory
        self.eventConsumer = eventConsumer
        self.logger = logger
        self.eventDispatcher = eventDispatcher

    async def _HandleWebSocketMessages(self, websocketConnection: WebSocketConnection, memberId: MemberId):
        while True:
            try:
                event = await websocketConnection.ReceiveDomainEvent()
                await self.eventDispatcher.Dispatch(event)
            except WebSocketDisconnect:
                self.logger.Info(f"WebSocket disconnected for member ID: {memberId}")
                self.websocketConnectionManager.Disconnect(memberId)
                break
            except DomainException as de:
                self.logger.Error(f"Error in WebSocket connection for member ID {memberId}: {str(de)}")
                exceptionEvent = await self.eventFactory.CreateFromDomainException(exception=de)
                await self.eventDispatcher.Dispatch(exceptionEvent)
                await websocketConnection.SendDomainEvent(exceptionEvent)
            except ValidationError as ve:
                self.logger.Error(f"Validation error in WebSocket connection for member ID {memberId}: {str(ve)}")
                exception = EventValidationError(message=str(ve))
                exceptionEvent = await self.eventFactory.CreateFromDomainException(exception=exception)
                await self.eventDispatcher.Dispatch(exceptionEvent)
                await websocketConnection.SendDomainEvent(exceptionEvent)
                # Do not disconnect on exceptions other than WebSocketDisconnect
            except Exception as ex:
                self.logger.Error(f"Unexpected error in WebSocket connection for member ID {memberId}: {str(ex)}")

    async def _HandleKafkaMessages(self, websocketConnection: WebSocketConnection, events: List[Type[DomainEvent]]):
        for event in events:
            self.eventConsumer.Subscribe(
                event=event,
                subscriber=WebSocketEventSubscriber(websocketConnection, self.logger),
            )
        try:
            await self.eventConsumer.Start()
        finally:
            await self.eventConsumer.Stop()

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

        # Create task for both handling websocket messages and kafka messages
        websocketTask = asyncio.create_task(self._HandleWebSocketMessages(websocketConnection, command.memberId))
        kafkaTask = asyncio.create_task(
            self._HandleKafkaMessages(
                websocketConnection,
                events=[  # List of events to subscribe to
                    MemberConnectedEvent,
                    # Add other event types as needed
                ],
            )
        )

        try:
            # Wait for either task to complete
            done, pending = await asyncio.wait(
                {websocketTask, kafkaTask},
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel any pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        finally:
            self.websocketConnectionManager.Disconnect(command.memberId)
            self.logger.Info(f"WebSocket connection closed for member ID: {command.memberId}")
