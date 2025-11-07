from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Type, TypeVar

from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent

T = TypeVar("T", bound=DomainEvent)


class IEventSubscriber(ABC, Generic[T]):
    """Interface for event subscribers."""

    @abstractmethod
    async def Handle(self, event: T) -> None:
        """Handle an incoming event."""


class IEventConsumer(ABC):
    """Interface for event consumers."""

    @abstractmethod
    async def Start(self, events: Optional[List[str]] = None) -> None:
        """Start the event consumer."""

    @abstractmethod
    async def Stop(self) -> None:
        """Stop the event consumer."""

    @abstractmethod
    def Subscribe(self, event: Type[DomainEvent], subscriber: IEventSubscriber) -> None:
        """Subscribe to a specific event type with a subscriber."""
