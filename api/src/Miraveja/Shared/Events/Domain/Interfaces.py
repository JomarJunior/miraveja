from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from Miraveja.Shared.Identifiers.Models import EventId


class DomainEvent(BaseModel, ABC):
    """Base class for domain events."""

    id: EventId = Field(default_factory=EventId.Generate, description="Unique identifier for the event")
    type: str = Field(..., description="Type of the event")
    aggregateId: str = Field(..., description="Identifier of the aggregate associated with the event")
    aggregateType: str = Field(..., description="Type of the aggregate associated with the event")
    version: int = Field(..., gt=0, description="Event schema version")
    occurredAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the event occurred"
    )

    def ToKafkaMessage(self) -> Dict[str, Any]:
        """
        Convert the domain event to a Kafka message format.

        Returns:
            Dict[str, Any]: The Kafka message representation of the event.
        """
        return {
            "eventId": str(self.id),
            "eventType": self.type,
            "aggregateId": self.aggregateId,
            "aggregateType": self.aggregateType,
            "version": self.version,
            "occurredAt": self.occurredAt.isoformat(),
            "payload": self.model_dump(exclude={"id", "type", "aggregateId", "aggregateType", "version", "occurredAt"}),
        }


class IEventProducer(ABC):
    """Interface for dispatchingf events to external systems."""

    @abstractmethod
    async def ProduceAll(self, events: List[DomainEvent]) -> None:
        """
        Produce all provided domain events to external systems.

        Args:
            events (List[DomainEvent]): List of domain events to be produced.
        """

    @abstractmethod
    async def Produce(self, event: DomainEvent) -> None:
        """
        Produce a single domain event to external systems.

        Args:
            event (DomainEvent): The domain event to be produced.
        """


class IEventEmitter(BaseModel, ABC):
    """Interface for emitting events within the system."""

    events: List[DomainEvent] = []

    @abstractmethod
    def EmitEvent(self, event: DomainEvent) -> None:
        """
        Emit a domain event within the system.

        Args:
            event (DomainEvent): The domain event to be emitted.
        """

    @abstractmethod
    def ReleaseEvents(self) -> List[DomainEvent]:
        """
        Release all emitted domain events and clear the internal event list.

        Returns:
            List[DomainEvent]: List of released domain events.
        """

    @abstractmethod
    def GetEvents(self) -> List[DomainEvent]:
        """
        Get all currently emitted domain events without clearing the internal event list.

        Returns:
            List[DomainEvent]: List of currently emitted domain events.
        """

    @abstractmethod
    def ClearEvents(self) -> None:
        """
        Clear all currently emitted domain events without returning them.
        """
