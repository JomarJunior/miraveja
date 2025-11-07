from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Union

from pydantic import BaseModel, Field, field_serializer, field_validator

from MiravejaCore.Shared.Identifiers.Models import EventId


class DomainEvent(BaseModel, ABC):
    """Base class for domain events."""

    id: EventId = Field(default_factory=EventId.Generate, description="Unique identifier for the event")
    type: ClassVar[str] = Field(..., description="Type of the event")
    aggregateId: str = Field(..., description="Identifier of the aggregate associated with the event")
    aggregateType: str = Field(..., description="Type of the aggregate associated with the event")
    version: ClassVar[int] = Field(..., gt=0, description="Event schema version")
    occurredAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Timestamp when the event occurred"
    )

    @field_validator("occurredAt", mode="before")
    @classmethod
    def ValidateOccurredAt(cls, value: Union[str, datetime]) -> datetime:
        if isinstance(value, str):
            return datetime.fromisoformat(value)

        return value

    @field_serializer("occurredAt")
    def SerializeOccurredAt(self, value: datetime) -> str:
        return value.isoformat()

    def ToKafkaMessage(self) -> Dict[str, Any]:
        """
        Convert the domain event to a Kafka message format.

        Returns:
            Dict[str, Any]: The Kafka message representation of the event.
        """
        return {
            "type": self.type,
            "version": self.version,
            "payload": self.model_dump(),
        }


class IEventProducer(ABC):
    """Interface for dispatching events to external systems."""

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

    events: List[DomainEvent] = Field(default_factory=list, description="List of emitted domain events", exclude=True)

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


class ISchemaRegistry(ABC):
    """Interface for managing event schemas."""

    @abstractmethod
    async def RegisterSchema(self, eventType: str, schema: Dict[str, Any]) -> None:
        """
        Register a new schema for a given event type.

        Args:
            eventType (str): The type of the event.
            schema (Dict[str, Any]): The schema definition for the event.
        """

    @abstractmethod
    async def GetSchema(self, eventType: str, eventVersion: int) -> Dict[str, Any]:
        """
        Retrieve the schema for a given event type.

        Args:
            eventType (str): The type of the event.
        Returns:
            Dict[str, Any]: The schema definition for the event.
        """
