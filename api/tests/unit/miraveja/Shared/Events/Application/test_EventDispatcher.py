import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import List, Optional

from Miraveja.Shared.Events.Application.EventDispatcher import EventDispatcher
from Miraveja.Shared.Events.Domain.Interfaces import DomainEvent, IEventProducer
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.Identifiers.Models import EventId


class TestEventDispatcher:
    """Test cases for EventDispatcher service."""

    def CreateMockEventProducer(self) -> MagicMock:
        """Create a mock event producer for testing."""
        mockProducer = MagicMock(spec=IEventProducer)
        mockProducer.ProduceAll = AsyncMock()
        mockProducer.Produce = AsyncMock()
        return mockProducer

    def CreateMockLogger(self) -> MagicMock:
        """Create a mock logger for testing."""
        mockLogger = MagicMock(spec=ILogger)
        return mockLogger

    def CreateTestDomainEvent(self, eventType: str = "test.event") -> DomainEvent:
        """Create a test domain event for testing purposes."""
        mockEvent = MagicMock(spec=DomainEvent)
        mockEvent.id = EventId.Generate()
        mockEvent.type = eventType
        mockEvent.aggregateId = "test-aggregate-id"
        mockEvent.aggregateType = "TestAggregate"
        mockEvent.version = 1
        # Configure the mock to return a string representation
        mockEvent.configure_mock(**{"__str__.return_value": f"MockEvent({eventType})"})
        return mockEvent

    def test_InitializeEventDispatcher_ShouldSetProducerAndLogger(self):
        """Test that EventDispatcher initializes with producer and logger."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()

        # Act
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        # Assert (using private attributes to verify initialization)
        assert dispatcher._eventProducer == mockProducer
        assert dispatcher._logger == mockLogger

    @pytest.mark.asyncio
    async def test_DispatchAllWithValidEvents_ShouldCallProducerAndLogInfo(self):
        """Test that DispatchAll dispatches events and logs appropriately."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        testEvents = [self.CreateTestDomainEvent("first.event"), self.CreateTestDomainEvent("second.event")]

        # Act
        await dispatcher.DispatchAll(testEvents)

        # Assert
        mockProducer.ProduceAll.assert_called_once_with(testEvents)
        mockLogger.Info.assert_any_call("Dispatching 2 events.")
        mockLogger.Info.assert_any_call("All events dispatched successfully.")

    @pytest.mark.asyncio
    async def test_DispatchAllWithEmptyList_ShouldLogInfoAndNotCallProducer(self):
        """Test that DispatchAll with empty list logs info and doesn't call producer."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        # Act
        await dispatcher.DispatchAll([])

        # Assert
        mockProducer.ProduceAll.assert_not_called()
        mockLogger.Info.assert_called_once_with("No events to dispatch.")

    @pytest.mark.asyncio
    async def test_DispatchAllWithFalsyList_ShouldLogInfoAndNotCallProducer(self):
        """Test that DispatchAll with falsy list logs info and doesn't call producer."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        # Act - Test with empty list (which is falsy)
        await dispatcher.DispatchAll([])

        # Assert
        mockProducer.ProduceAll.assert_not_called()
        mockLogger.Info.assert_called_once_with("No events to dispatch.")

    @pytest.mark.asyncio
    async def test_DispatchAllWithProducerException_ShouldLogErrorAndReraise(self):
        """Test that DispatchAll handles producer exceptions correctly."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        testError = Exception("Producer connection failed")
        mockProducer.ProduceAll.side_effect = testError

        testEvents = [self.CreateTestDomainEvent("error.event")]

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await dispatcher.DispatchAll(testEvents)

        assert exc_info.value == testError
        mockProducer.ProduceAll.assert_called_once_with(testEvents)
        mockLogger.Info.assert_any_call("Dispatching 1 events.")
        mockLogger.Error.assert_called_once_with(f"Failed to dispatch events: {testError}")

    @pytest.mark.asyncio
    async def test_DispatchWithValidEvent_ShouldCallProducerAndLogInfo(self):
        """Test that Dispatch dispatches single event and logs appropriately."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        testEvent = self.CreateTestDomainEvent("single.event")

        # Act
        await dispatcher.Dispatch(testEvent)

        # Assert
        mockProducer.Produce.assert_called_once_with(testEvent)
        mockLogger.Info.assert_any_call(f"Dispatching event: {testEvent}")
        mockLogger.Info.assert_any_call("Event dispatched successfully.")

    @pytest.mark.asyncio
    async def test_DispatchWithNoneEvent_ShouldLogWarningAndNotCallProducer(self):
        """Test that Dispatch with None event logs warning and doesn't call producer."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        # Act - Cast None to Optional[DomainEvent] to bypass type checking for test
        noneEvent: Optional[DomainEvent] = None
        await dispatcher.Dispatch(noneEvent)  # type: ignore

        # Assert
        mockProducer.Produce.assert_not_called()
        mockLogger.Warning.assert_called_once_with("No event to dispatch.")

    @pytest.mark.asyncio
    async def test_DispatchWithProducerException_ShouldLogErrorAndReraise(self):
        """Test that Dispatch handles producer exceptions correctly."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        testError = RuntimeError("Kafka connection timeout")
        mockProducer.Produce.side_effect = testError

        testEvent = self.CreateTestDomainEvent("timeout.event")

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await dispatcher.Dispatch(testEvent)

        assert exc_info.value == testError
        mockProducer.Produce.assert_called_once_with(testEvent)
        mockLogger.Info.assert_any_call(f"Dispatching event: {testEvent}")
        mockLogger.Error.assert_called_once_with(f"Failed to dispatch event: {testError}")

    @pytest.mark.asyncio
    async def test_DispatchAllWithSingleEvent_ShouldLogCorrectEventCount(self):
        """Test that DispatchAll with single event logs correct count."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        testEvents = [self.CreateTestDomainEvent("single.in.list")]

        # Act
        await dispatcher.DispatchAll(testEvents)

        # Assert
        mockProducer.ProduceAll.assert_called_once_with(testEvents)
        mockLogger.Info.assert_any_call("Dispatching 1 events.")
        mockLogger.Info.assert_any_call("All events dispatched successfully.")

    @pytest.mark.asyncio
    async def test_DispatchAllWithMultipleEvents_ShouldLogCorrectEventCount(self):
        """Test that DispatchAll with multiple events logs correct count."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        testEvents = [
            self.CreateTestDomainEvent("event.one"),
            self.CreateTestDomainEvent("event.two"),
            self.CreateTestDomainEvent("event.three"),
            self.CreateTestDomainEvent("event.four"),
            self.CreateTestDomainEvent("event.five"),
        ]

        # Act
        await dispatcher.DispatchAll(testEvents)

        # Assert
        mockProducer.ProduceAll.assert_called_once_with(testEvents)
        mockLogger.Info.assert_any_call("Dispatching 5 events.")
        mockLogger.Info.assert_any_call("All events dispatched successfully.")

    @pytest.mark.asyncio
    async def test_DispatchAllThenDispatch_ShouldCallBothMethods(self):
        """Test that DispatchAll and Dispatch can be called sequentially."""
        # Arrange
        mockProducer = self.CreateMockEventProducer()
        mockLogger = self.CreateMockLogger()
        dispatcher = EventDispatcher(mockProducer, mockLogger)

        batchEvents = [self.CreateTestDomainEvent("batch.event")]
        singleEvent = self.CreateTestDomainEvent("single.event")

        # Act
        await dispatcher.DispatchAll(batchEvents)
        await dispatcher.Dispatch(singleEvent)

        # Assert
        mockProducer.ProduceAll.assert_called_once_with(batchEvents)
        mockProducer.Produce.assert_called_once_with(singleEvent)

        # Verify info logs for both operations
        assert mockLogger.Info.call_count >= 4  # At least 2 calls for each operation
