from typing import List

from Miraveja.Shared.Events.Domain.Interfaces import DomainEvent, IEventEmitter


class EventEmitter(IEventEmitter):
    """Mixin class to provide event emitting capabilities."""

    def GetEvents(self) -> List[DomainEvent]:
        """Get all currently emitted domain events without clearing the internal event list."""
        return self.events

    def EmitEvent(self, event: DomainEvent) -> None:
        """Emit a domain event within the system."""
        self.events.append(event)

    def ReleaseEvents(self) -> List[DomainEvent]:
        """Release all emitted domain events and clear the internal event list."""
        releasedEvents = self.events.copy()
        self.events.clear()
        return releasedEvents

    def ClearEvents(self) -> None:
        """Clear all currently emitted domain events without returning them."""
        self.events.clear()
