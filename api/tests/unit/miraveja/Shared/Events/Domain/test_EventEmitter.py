import pytest
from unittest.mock import MagicMock

from Miraveja.Shared.Events.Domain.Models import EventEmitter
from Miraveja.Shared.Events.Domain.Interfaces import DomainEvent
from Miraveja.Shared.Identifiers.Models import EventId


class TestEventEmitter:
    """Test cases for EventEmitter model."""

    def CreateTestDomainEvent(self, eventType: str = "test.event") -> DomainEvent:
        """Create a test domain event for testing purposes."""
        # Create a mock DomainEvent since it's abstract
        mockEvent = MagicMock(spec=DomainEvent)
        mockEvent.id = EventId.Generate()
        mockEvent.type = eventType
        mockEvent.aggregateId = "test-aggregate-id"
        mockEvent.aggregateType = "TestAggregate"
        mockEvent.version = 1
        return mockEvent

    def test_InitializeEventEmitter_ShouldHaveEmptyEventsList(self):
        """Test that EventEmitter initializes with an empty events list."""
        # Arrange & Act
        eventEmitter = EventEmitter()

        # Assert
        assert eventEmitter.events == []
        assert len(eventEmitter.GetEvents()) == 0

    def test_EmitEventWithValidEvent_ShouldAddEventToList(self):
        """Test that EmitEvent adds a valid event to the events list."""
        # Arrange
        eventEmitter = EventEmitter()
        testEvent = self.CreateTestDomainEvent("test.event.created")

        # Act
        eventEmitter.EmitEvent(testEvent)

        # Assert
        events = eventEmitter.GetEvents()
        assert len(events) == 1
        assert events[0] == testEvent

    def test_EmitMultipleEvents_ShouldAddAllEventsToList(self):
        """Test that multiple EmitEvent calls add all events to the list."""
        # Arrange
        eventEmitter = EventEmitter()
        firstEvent = self.CreateTestDomainEvent("first.event")
        secondEvent = self.CreateTestDomainEvent("second.event")
        thirdEvent = self.CreateTestDomainEvent("third.event")

        # Act
        eventEmitter.EmitEvent(firstEvent)
        eventEmitter.EmitEvent(secondEvent)
        eventEmitter.EmitEvent(thirdEvent)

        # Assert
        events = eventEmitter.GetEvents()
        assert len(events) == 3
        assert events[0] == firstEvent
        assert events[1] == secondEvent
        assert events[2] == thirdEvent

    def test_GetEventsAfterEmittingEvents_ShouldReturnAllEventsWithoutClearing(self):
        """Test that GetEvents returns all events without clearing the internal list."""
        # Arrange
        eventEmitter = EventEmitter()
        testEvent = self.CreateTestDomainEvent("persistent.event")
        eventEmitter.EmitEvent(testEvent)

        # Act
        firstRetrieval = eventEmitter.GetEvents()
        secondRetrieval = eventEmitter.GetEvents()

        # Assert
        assert len(firstRetrieval) == 1
        assert len(secondRetrieval) == 1
        assert firstRetrieval[0] == testEvent
        assert secondRetrieval[0] == testEvent
        # Verify internal list is not cleared
        assert len(eventEmitter.events) == 1

    def test_ReleaseEventsWithEmittedEvents_ShouldReturnEventsAndClearList(self):
        """Test that ReleaseEvents returns all events and clears the internal list."""
        # Arrange
        eventEmitter = EventEmitter()
        firstEvent = self.CreateTestDomainEvent("release.event.first")
        secondEvent = self.CreateTestDomainEvent("release.event.second")
        eventEmitter.EmitEvent(firstEvent)
        eventEmitter.EmitEvent(secondEvent)

        # Act
        releasedEvents = eventEmitter.ReleaseEvents()

        # Assert
        assert len(releasedEvents) == 2
        assert releasedEvents[0] == firstEvent
        assert releasedEvents[1] == secondEvent
        # Verify internal list is cleared
        assert len(eventEmitter.events) == 0
        assert len(eventEmitter.GetEvents()) == 0

    def test_ReleaseEventsWithNoEvents_ShouldReturnEmptyListAndRemainEmpty(self):
        """Test that ReleaseEvents returns empty list when no events are emitted."""
        # Arrange
        eventEmitter = EventEmitter()

        # Act
        releasedEvents = eventEmitter.ReleaseEvents()

        # Assert
        assert releasedEvents == []
        assert len(eventEmitter.events) == 0

    def test_ClearEventsWithEmittedEvents_ShouldClearListWithoutReturning(self):
        """Test that ClearEvents clears the events list without returning them."""
        # Arrange
        eventEmitter = EventEmitter()
        testEvent = self.CreateTestDomainEvent("clear.event")
        eventEmitter.EmitEvent(testEvent)

        # Verify event was added
        assert len(eventEmitter.GetEvents()) == 1

        # Act
        result = eventEmitter.ClearEvents()

        # Assert
        assert result is None
        assert len(eventEmitter.events) == 0
        assert len(eventEmitter.GetEvents()) == 0

    def test_ClearEventsWithNoEvents_ShouldRemainEmptyWithoutReturning(self):
        """Test that ClearEvents on empty list remains empty without returning anything."""
        # Arrange
        eventEmitter = EventEmitter()

        # Act
        result = eventEmitter.ClearEvents()

        # Assert
        assert result is None
        assert len(eventEmitter.events) == 0

    def test_ReleaseEventsAfterClearEvents_ShouldReturnEmptyList(self):
        """Test that ReleaseEvents after ClearEvents returns empty list."""
        # Arrange
        eventEmitter = EventEmitter()
        testEvent = self.CreateTestDomainEvent("clear.then.release")
        eventEmitter.EmitEvent(testEvent)
        eventEmitter.ClearEvents()

        # Act
        releasedEvents = eventEmitter.ReleaseEvents()

        # Assert
        assert releasedEvents == []
        assert len(eventEmitter.events) == 0

    def test_EmitEventAfterReleaseEvents_ShouldStartFreshEventsList(self):
        """Test that EmitEvent after ReleaseEvents starts a fresh events list."""
        # Arrange
        eventEmitter = EventEmitter()
        firstEvent = self.CreateTestDomainEvent("first.batch")
        eventEmitter.EmitEvent(firstEvent)
        eventEmitter.ReleaseEvents()

        secondEvent = self.CreateTestDomainEvent("second.batch")

        # Act
        eventEmitter.EmitEvent(secondEvent)

        # Assert
        events = eventEmitter.GetEvents()
        assert len(events) == 1
        assert events[0] == secondEvent
        assert events[0] != firstEvent
