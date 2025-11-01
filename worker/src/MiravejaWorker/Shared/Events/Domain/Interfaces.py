from abc import ABC, abstractmethod
from typing import List, Optional, Type

from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent


class IEventSubscriber(ABC):
    """Interface for event subscribers."""

    @abstractmethod
    async def Handle(self, event: DomainEvent) -> None:
        """Handle an incoming event."""


class IEventConsumer(ABC):
    """Interface for event consumers."""

    @abstractmethod
    async def Start(self, topics: Optional[List[str]] = None) -> None:
        """Start the event consumer."""

    @abstractmethod
    async def Stop(self) -> None:
        """Stop the event consumer."""

    @abstractmethod
    def Subscribe(self, event: Type[DomainEvent], subscriber: IEventSubscriber, topic: Optional[str] = None) -> None:
        """Subscribe to a specific event type with a subscriber."""
