from datetime import datetime, timezone
import json
from typing import Dict, Optional
from pydantic import BaseModel, Field, field_serializer
from fastapi import WebSocket

from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Events.Domain.Services import EventFactory
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent


class WebSocketConnection(BaseModel):
    memberId: MemberId = Field(..., description="The ID of the member associated with the connection")
    connection: WebSocket = Field(
        ..., description="The WebSocket connection instance", exclude=True
    )  # * This triggers pydantic error "Unable to generate pydantic-core schema..."
    openedAt: Optional[datetime] = Field(description="The time when the connection was opened", default=None)
    eventFactory: EventFactory = Field(..., description="Factory to create domain events", exclude=True)

    @field_serializer("openedAt")
    @classmethod
    def SerializeOpenedAt(cls, v: Optional[datetime]) -> Optional[str]:
        if v is None:
            return None
        return v.isoformat()

    # * To avoid the error, we need to:
    model_config = {
        "arbitrary_types_allowed": True,  # Allow arbitrary types
    }

    async def Accept(self):
        self.openedAt = datetime.now(timezone.utc)
        return await self.connection.accept()

    async def Close(self):
        return await self.connection.close()

    async def SendDomainEvent(self, event: DomainEvent):
        data = event.ToKafkaMessage()
        await self.connection.send_text(json.dumps(data))

    async def ReceiveDomainEvent(self) -> DomainEvent:
        data = await self.connection.receive_text()
        event = await self.eventFactory.CreateFromJson(data)

        return event


class WebSocketConnectionManager(BaseModel):
    connections: Dict[MemberId, WebSocketConnection] = Field(
        default_factory=dict, description="Active WebSocket connections", exclude=True
    )
    logger: ILogger = Field(
        ..., description="Logger instance for logging connection events", exclude=True
    )  # * Another pydantic arbitrary type

    # *
    model_config = {
        "arbitrary_types_allowed": True,  # Allow arbitrary types
    }

    def Connect(self, connection: WebSocketConnection):
        self.connections[connection.memberId] = connection

    def Disconnect(self, memberId: MemberId):
        if memberId in self.connections:
            del self.connections[memberId]

    async def SendEventToMember(self, memberId: MemberId, event: DomainEvent):
        """Send an event to a specific connected member."""
        connection = self.connections.get(memberId)
        if connection is None:
            self.logger.Warning(f"No active connection for member ID: {memberId}")
            return

        await connection.SendDomainEvent(event)

    async def BroadcastEvent(self, event: DomainEvent):
        """Send an event to all connected members."""
        for connection in self.connections.values():
            await connection.SendDomainEvent(event)
