import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from typing import ClassVar, Dict, List, Optional, Type, Union
import json

from MiravejaCore.Shared.Events.Infrastructure.Kafka.Services import KafkaEventConsumer, KafkaEventProducer
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig, ConsumerConfig
from MiravejaCore.Shared.Events.Domain.Enums import ConsumerAutoOffsetReset
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent, IEventSubscriber
from MiravejaCore.Shared.Events.Domain.Services import EventFactory, EventRegistry, EventDeserializerService
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Identifiers.Models import EventId


class TestDomainEvent(DomainEvent):
    """Test domain event for testing purposes."""

    type: ClassVar[str] = "test.event"
    aggregateType: str = "TestAggregate"
    aggregateId: str = "test-123"
    version: ClassVar[int] = 1
    testField: str = "test_value"


class UserRegisteredEvent(DomainEvent):
    """Test event for user registration."""

    type: ClassVar[str] = "user.registered"
    aggregateType: str = "User"
    aggregateId: str = "user-123"
    version: ClassVar[int] = 1
    email: str = "test@example.com"


class OrderCreatedEvent(DomainEvent):
    """Test event for order creation."""

    type: ClassVar[str] = "order.created"
    aggregateType: str = "Order"
    aggregateId: str = "order-456"
    version: ClassVar[int] = 1
    amount: float = 100.0


class TestKafkaEventConsumer:
    """Test cases for KafkaEventConsumer service."""

    def CreateTestKafkaConfig(
        self,
        bootstrapServers: str = "localhost:9092",
        topicPrefix: str = "test",
        groupId: str = "test-group",
    ) -> KafkaConfig:
        """Create a test Kafka configuration."""
        return KafkaConfig(
            bootstrapServers=bootstrapServers,
            topicPrefix=topicPrefix,
            consumer=ConsumerConfig(
                groupId=groupId,
                autoOffsetReset=ConsumerAutoOffsetReset.EARLIEST,
                enableAutoCommit=True,
                autoCommitIntervalMillis=5000,
                sessionTimeoutMillis=10000,
                heartbeatIntervalMillis=3000,
            ),
        )

    def CreateMockLogger(self) -> ILogger:
        """Create a mock logger for testing."""
        mockLogger = Mock(spec=ILogger)
        mockLogger.Error = Mock()
        mockLogger.Info = Mock()
        mockLogger.Debug = Mock()
        return mockLogger

    def CreateMockEventFactory(self) -> EventFactory:
        """Create a mock event factory for testing."""
        mockFactory = AsyncMock(spec=EventFactory)
        return mockFactory

    def CreateMockEventSubscriber(self) -> IEventSubscriber:
        """Create a mock event subscriber for testing."""
        mockSubscriber = AsyncMock(spec=IEventSubscriber)
        mockSubscriber.Handle = AsyncMock()
        return mockSubscriber

    def test_InitializeWithValidDependencies_ShouldSetCorrectValues(self):
        """Test that KafkaEventConsumer initializes with valid dependencies."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        # Act
        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Assert
        assert consumer._config == testConfig
        assert consumer._logger == mockLogger
        assert consumer._eventFactory == mockFactory
        assert consumer._eventHandlers == {}
        assert consumer._events == set()
        assert consumer._totalSubscribers == 0
        assert consumer._consumer is None

    def test_SubscribeWithEventType_ShouldAddSubscriberToHandlers(self):
        """Test that Subscribe adds subscriber to event handlers correctly."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber = self.CreateMockEventSubscriber()

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        consumer.Subscribe(TestDomainEvent, mockSubscriber)

        # Assert
        topicName = testConfig.GetTopicName("test.event", 1)
        assert topicName in consumer._eventHandlers
        assert len(consumer._eventHandlers[topicName]) == 1
        assert consumer._eventHandlers[topicName][0] == mockSubscriber
        assert topicName in consumer._events
        assert consumer._totalSubscribers == 1
        mockLogger.Info.assert_called_with("Subscriber added for event: test.event")

    def test_SubscribeWithStringEventType_ShouldAddSubscriberCorrectly(self):
        """Test that Subscribe handles string event types."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber = self.CreateMockEventSubscriber()

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        consumer.Subscribe("custom.event", mockSubscriber)

        # Assert
        topicName = testConfig.GetTopicName("custom.event", 1)
        assert topicName in consumer._eventHandlers
        assert len(consumer._eventHandlers[topicName]) == 1
        mockLogger.Info.assert_called_with("Subscriber added for event: custom.event")

    def test_SubscribeMultipleSubscribersToSameEvent_ShouldAddAllSubscribers(self):
        """Test that Subscribe adds multiple subscribers to the same event."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber1 = self.CreateMockEventSubscriber()
        mockSubscriber2 = self.CreateMockEventSubscriber()
        mockSubscriber3 = self.CreateMockEventSubscriber()

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        consumer.Subscribe(TestDomainEvent, mockSubscriber1)
        consumer.Subscribe(TestDomainEvent, mockSubscriber2)
        consumer.Subscribe(TestDomainEvent, mockSubscriber3)

        # Assert
        topicName = testConfig.GetTopicName("test.event", 1)
        assert len(consumer._eventHandlers[topicName]) == 3
        assert consumer._totalSubscribers == 3

    def test_SubscribeToDifferentEvents_ShouldMaintainSeparateHandlers(self):
        """Test that Subscribe maintains separate handlers for different events."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber1 = self.CreateMockEventSubscriber()
        mockSubscriber2 = self.CreateMockEventSubscriber()

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        consumer.Subscribe(UserRegisteredEvent, mockSubscriber1)
        consumer.Subscribe(OrderCreatedEvent, mockSubscriber2)

        # Assert
        userTopic = testConfig.GetTopicName("user.registered", 1)
        orderTopic = testConfig.GetTopicName("order.created", 1)

        assert userTopic in consumer._eventHandlers
        assert orderTopic in consumer._eventHandlers
        assert len(consumer._eventHandlers[userTopic]) == 1
        assert len(consumer._eventHandlers[orderTopic]) == 1
        assert consumer._totalSubscribers == 2

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaConsumer")
    @pytest.mark.asyncio
    async def test_StartWithNoEvents_ShouldInitializeConsumer(self, mock_aiokafka_consumer):
        """Test that Start initializes consumer with no events."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        # Create async generator that yields nothing
        async def EmptyAsyncGenerator():
            return
            yield  # This line is never reached but makes it a generator

        # Create mock consumer instance that immediately stops
        mockConsumerInstance = AsyncMock()
        mockConsumerInstance.start = AsyncMock()
        mockConsumerInstance.stop = AsyncMock()
        mockConsumerInstance.__aiter__ = lambda self: EmptyAsyncGenerator()
        mock_aiokafka_consumer.return_value = mockConsumerInstance

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        await consumer.Start([])

        # Assert
        mockConsumerInstance.start.assert_called_once()
        mockConsumerInstance.stop.assert_called_once()
        assert mockLogger.Info.call_count >= 2

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaConsumer")
    @pytest.mark.asyncio
    async def test_StartWithSpecificEvents_ShouldListenToThoseEvents(self, mock_aiokafka_consumer):
        """Test that Start listens to specific events when provided."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        # Create async generator that yields nothing
        async def EmptyAsyncGenerator():
            return
            yield

        mockConsumerInstance = AsyncMock()
        mockConsumerInstance.start = AsyncMock()
        mockConsumerInstance.stop = AsyncMock()
        mockConsumerInstance.__aiter__ = lambda self: EmptyAsyncGenerator()
        mock_aiokafka_consumer.return_value = mockConsumerInstance

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        testEvents = ["test.event.1.v1", "test.event.2.v1"]

        # Act
        await consumer.Start(events=testEvents)

        # Assert
        mock_aiokafka_consumer.assert_called_once()

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaConsumer")
    @pytest.mark.asyncio
    async def test_StartWithSubscribedEvents_ShouldUseRegisteredEvents(self, mock_aiokafka_consumer):
        """Test that Start uses registered events when no specific events provided."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber = self.CreateMockEventSubscriber()

        # Create async generator that yields nothing
        async def EmptyAsyncGenerator():
            return
            yield

        mockConsumerInstance = AsyncMock()
        mockConsumerInstance.start = AsyncMock()
        mockConsumerInstance.stop = AsyncMock()
        mockConsumerInstance.__aiter__ = lambda self: EmptyAsyncGenerator()
        mock_aiokafka_consumer.return_value = mockConsumerInstance

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Subscribe to events first
        consumer.Subscribe(UserRegisteredEvent, mockSubscriber)
        consumer.Subscribe(OrderCreatedEvent, mockSubscriber)

        # Act
        await consumer.Start()

        # Assert
        mockConsumerInstance.start.assert_called_once()
        # Should listen to subscribed events
        assert len(consumer._events) == 2

    @pytest.mark.asyncio
    async def test_StopWithInitializedConsumer_ShouldStopConsumer(self):
        """Test that Stop stops the consumer when initialized."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Mock the consumer
        mockConsumerInstance = AsyncMock()
        mockConsumerInstance.stop = AsyncMock()
        consumer._consumer = mockConsumerInstance

        # Act
        await consumer.Stop()

        # Assert
        mockConsumerInstance.stop.assert_called_once()
        mockLogger.Info.assert_called_with("KafkaEventConsumer stopped.")

    @pytest.mark.asyncio
    async def test_StopWithUninitializedConsumer_ShouldNotRaiseError(self):
        """Test that Stop handles uninitialized consumer gracefully."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)
        consumer._consumer = None

        # Act & Assert - should not raise error
        await consumer.Stop()

    @pytest.mark.asyncio
    async def test_ProcessMessageWithValidEvent_ShouldDeserializeAndDispatch(self):
        """Test that _ProcessMessage deserializes event and dispatches to subscribers."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber = self.CreateMockEventSubscriber()

        # Create mock event
        mockEvent = TestDomainEvent(aggregateType="TestAggregate", aggregateId="test-123")
        mockFactory.CreateFromData = AsyncMock(return_value=mockEvent)

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Subscribe to the event
        topicName = testConfig.GetTopicName("test.event", 1)
        consumer.Subscribe(TestDomainEvent, mockSubscriber)

        # Create mock Kafka message
        mockMessage = MagicMock()
        mockMessage.topic = topicName
        mockMessage.value = {"type": "test.event", "version": 1, "payload": {"testField": "test_value"}}

        # Act
        await consumer._ProcessMessage(mockMessage)

        # Assert
        mockFactory.CreateFromData.assert_called_once_with(mockMessage.value)
        mockSubscriber.Handle.assert_called_once_with(mockEvent)
        mockLogger.Debug.assert_called_once()

    @pytest.mark.asyncio
    async def test_ProcessMessageWithMultipleSubscribers_ShouldDispatchToAll(self):
        """Test that _ProcessMessage dispatches event to all registered subscribers."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber1 = self.CreateMockEventSubscriber()
        mockSubscriber2 = self.CreateMockEventSubscriber()
        mockSubscriber3 = self.CreateMockEventSubscriber()

        mockEvent = TestDomainEvent(aggregateType="TestAggregate", aggregateId="test-123")
        mockFactory.CreateFromData = AsyncMock(return_value=mockEvent)

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Subscribe multiple subscribers
        consumer.Subscribe(TestDomainEvent, mockSubscriber1)
        consumer.Subscribe(TestDomainEvent, mockSubscriber2)
        consumer.Subscribe(TestDomainEvent, mockSubscriber3)

        # Create mock Kafka message
        topicName = testConfig.GetTopicName("test.event", 1)
        mockMessage = MagicMock()
        mockMessage.topic = topicName
        mockMessage.value = {"type": "test.event", "version": 1, "payload": {}}

        # Act
        await consumer._ProcessMessage(mockMessage)

        # Assert
        mockSubscriber1.Handle.assert_called_once_with(mockEvent)
        mockSubscriber2.Handle.assert_called_once_with(mockEvent)
        mockSubscriber3.Handle.assert_called_once_with(mockEvent)

    @pytest.mark.asyncio
    async def test_ProcessMessageWithNoSubscribers_ShouldDeserializeButNotDispatch(self):
        """Test that _ProcessMessage deserializes event even without subscribers."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        mockEvent = TestDomainEvent(aggregateType="TestAggregate", aggregateId="test-123")
        mockFactory.CreateFromData = AsyncMock(return_value=mockEvent)

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Create mock Kafka message for unsubscribed topic
        mockMessage = MagicMock()
        mockMessage.topic = "test.unsubscribed.event.v1"
        mockMessage.value = {"type": "unsubscribed.event", "version": 1, "payload": {}}

        # Act
        await consumer._ProcessMessage(mockMessage)

        # Assert
        mockFactory.CreateFromData.assert_called_once_with(mockMessage.value)

    @pytest.mark.asyncio
    async def test_ProcessMessageWithException_ShouldLogError(self):
        """Test that _ProcessMessage logs errors when event processing fails."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        # Make CreateFromData raise an exception
        testError = Exception("Deserialization error")
        mockFactory.CreateFromData = AsyncMock(side_effect=testError)

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Create mock Kafka message
        mockMessage = MagicMock()
        mockMessage.topic = "test.event.v1"
        mockMessage.value = {"type": "test.event", "version": 1, "payload": {}}

        # Act
        await consumer._ProcessMessage(mockMessage)

        # Assert
        mockLogger.Error.assert_called_once()
        assert "Error processing message" in mockLogger.Error.call_args[0][0]

    @pytest.mark.asyncio
    async def test_ProcessMessageWithSubscriberException_ShouldLogError(self):
        """Test that _ProcessMessage logs errors when subscriber handling fails."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber = self.CreateMockEventSubscriber()

        mockEvent = TestDomainEvent(aggregateType="TestAggregate", aggregateId="test-123")
        mockFactory.CreateFromData = AsyncMock(return_value=mockEvent)

        # Make subscriber.Handle raise an exception
        testError = Exception("Handler error")
        mockSubscriber.Handle = AsyncMock(side_effect=testError)

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)
        consumer.Subscribe(TestDomainEvent, mockSubscriber)

        # Create mock Kafka message
        topicName = testConfig.GetTopicName("test.event", 1)
        mockMessage = MagicMock()
        mockMessage.topic = topicName
        mockMessage.value = {"type": "test.event", "version": 1, "payload": {}}

        # Act
        await consumer._ProcessMessage(mockMessage)

        # Assert
        mockLogger.Error.assert_called_once()


class TestKafkaEventConsumerEdgeCases:
    """Test edge cases for KafkaEventConsumer."""

    def CreateTestKafkaConfig(self) -> KafkaConfig:
        """Create a test Kafka configuration."""
        return KafkaConfig(
            bootstrapServers="localhost:9092",
            topicPrefix="test",
            consumer=ConsumerConfig(groupId="test-group"),
        )

    def CreateMockLogger(self) -> ILogger:
        """Create a mock logger for testing."""
        mockLogger = Mock(spec=ILogger)
        mockLogger.Error = Mock()
        mockLogger.Info = Mock()
        mockLogger.Debug = Mock()
        return mockLogger

    def CreateMockEventFactory(self) -> EventFactory:
        """Create a mock event factory for testing."""
        return AsyncMock(spec=EventFactory)

    def CreateMockEventSubscriber(self) -> IEventSubscriber:
        """Create a mock event subscriber for testing."""
        mockSubscriber = AsyncMock(spec=IEventSubscriber)
        mockSubscriber.Handle = AsyncMock()
        return mockSubscriber

    def test_SubscribeWithSameSubscriberMultipleTimes_ShouldAddEachTime(self):
        """Test that subscribing the same subscriber multiple times adds it each time."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber = self.CreateMockEventSubscriber()

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        consumer.Subscribe(TestDomainEvent, mockSubscriber)
        consumer.Subscribe(TestDomainEvent, mockSubscriber)

        # Assert
        topicName = testConfig.GetTopicName("test.event", 1)
        assert len(consumer._eventHandlers[topicName]) == 2
        assert consumer._totalSubscribers == 2

    def test_SubscribeWithEmptyStringEventType_ShouldHandleGracefully(self):
        """Test that Subscribe handles empty string event type."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber = self.CreateMockEventSubscriber()

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        consumer.Subscribe("", mockSubscriber)

        # Assert
        topicName = testConfig.GetTopicName("", 1)
        assert topicName in consumer._eventHandlers
        assert consumer._totalSubscribers == 1

    @pytest.mark.asyncio
    async def test_ProcessMessageWithEmptyValue_ShouldHandleGracefully(self):
        """Test that _ProcessMessage handles empty message value."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        mockFactory.CreateFromData = AsyncMock(side_effect=Exception("Empty value"))

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Create mock Kafka message with empty value
        mockMessage = MagicMock()
        mockMessage.topic = "test.event.v1"
        mockMessage.value = {}

        # Act
        await consumer._ProcessMessage(mockMessage)

        # Assert
        mockLogger.Error.assert_called_once()

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaConsumer")
    @pytest.mark.asyncio
    async def test_StartWithConfiguredGroupId_ShouldUseGroupId(self, mock_aiokafka_consumer):
        """Test that Start uses the configured group ID from config."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        testConfig.consumer.groupId = "custom-consumer-group"
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        # Create async generator that yields nothing
        async def EmptyAsyncGenerator():
            return
            yield

        mockConsumerInstance = AsyncMock()
        mockConsumerInstance.start = AsyncMock()
        mockConsumerInstance.stop = AsyncMock()
        mockConsumerInstance.__aiter__ = lambda self: EmptyAsyncGenerator()
        mock_aiokafka_consumer.return_value = mockConsumerInstance

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        await consumer.Start([])

        # Assert
        call_kwargs = mock_aiokafka_consumer.call_args[1]
        assert call_kwargs["group_id"] == "custom-consumer-group"

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaConsumer")
    @pytest.mark.asyncio
    async def test_StartWithDeserializerError_ShouldLogError(self, mock_aiokafka_consumer):
        """Test that Start handles deserializer errors gracefully."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        # Create async generator that yields nothing
        async def EmptyAsyncGenerator():
            return
            yield

        mockConsumerInstance = AsyncMock()
        mockConsumerInstance.start = AsyncMock()
        mockConsumerInstance.stop = AsyncMock()
        mockConsumerInstance.__aiter__ = lambda self: EmptyAsyncGenerator()
        mock_aiokafka_consumer.return_value = mockConsumerInstance

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        await consumer.Start([])

        # Assert - deserializer should be defined
        mock_aiokafka_consumer.assert_called_once()
        call_kwargs = mock_aiokafka_consumer.call_args[1]
        assert "value_deserializer" in call_kwargs

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaConsumer")
    @pytest.mark.asyncio
    async def test_StartWithMessageProcessing_ShouldProcessMessages(self, mock_aiokafka_consumer):
        """Test that Start processes messages from the consumer."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber = self.CreateMockEventSubscriber()

        # Create mock event
        mockEvent = TestDomainEvent(aggregateType="TestAggregate", aggregateId="test-123")
        mockFactory.CreateFromData = AsyncMock(return_value=mockEvent)

        # Create mock Kafka message
        mockMessage = MagicMock()
        topicName = testConfig.GetTopicName("test.event", 1)
        mockMessage.topic = topicName
        mockMessage.value = {"type": "test.event", "version": 1, "payload": {}}

        # Create async generator that yields one message
        async def MessageAsyncGenerator():
            yield mockMessage

        mockConsumerInstance = AsyncMock()
        mockConsumerInstance.start = AsyncMock()
        mockConsumerInstance.stop = AsyncMock()
        mockConsumerInstance.__aiter__ = lambda self: MessageAsyncGenerator()
        mock_aiokafka_consumer.return_value = mockConsumerInstance

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)
        consumer.Subscribe(TestDomainEvent, mockSubscriber)

        # Act
        await consumer.Start([topicName])

        # Assert
        mockFactory.CreateFromData.assert_called_once_with(mockMessage.value)
        mockSubscriber.Handle.assert_called_once_with(mockEvent)

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaConsumer")
    @pytest.mark.asyncio
    async def test_StartWithDeserializationError_ShouldReturnEmptyDict(self, mock_aiokafka_consumer):
        """Test that deserializer returns empty dict on JSON decode error."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        # Capture the deserializer function
        capturedDeserializer = None

        def CaptureDeserializer(*args, **kwargs):
            nonlocal capturedDeserializer
            if "value_deserializer" in kwargs:
                capturedDeserializer = kwargs["value_deserializer"]
            mockInstance = AsyncMock()
            mockInstance.start = AsyncMock()
            mockInstance.stop = AsyncMock()

            async def EmptyGen():
                return
                yield

            mockInstance.__aiter__ = lambda self: EmptyGen()
            return mockInstance

        mock_aiokafka_consumer.side_effect = CaptureDeserializer

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        await consumer.Start([])

        # Test the deserializer with invalid JSON
        invalidJson = b"invalid json {{"
        result = capturedDeserializer(invalidJson)

        # Assert
        assert result == {}
        assert mockLogger.Error.call_count >= 1

    def test_SubscribeWithMultipleEventsOfDifferentVersions_ShouldTrackSeparately(self):
        """Test that Subscribe tracks different versions separately."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockSubscriber1 = self.CreateMockEventSubscriber()
        mockSubscriber2 = self.CreateMockEventSubscriber()

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act - Subscribe to same event type multiple times
        consumer.Subscribe("event.type", mockSubscriber1)
        consumer.Subscribe("event.type", mockSubscriber2)

        # Assert
        # Both should be in the same topic (v1 by default)
        topicV1 = testConfig.GetTopicName("event.type", 1)
        assert topicV1 in consumer._eventHandlers
        assert len(consumer._eventHandlers[topicV1]) == 2
        assert consumer._totalSubscribers == 2

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaConsumer")
    @pytest.mark.asyncio
    async def test_StartWithValidJsonMessage_ShouldDeserializeSuccessfully(self, mock_aiokafka_consumer):
        """Test that Start deserializes valid JSON messages successfully."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()

        capturedDeserializer = None

        def CaptureDeserializer(*args, **kwargs):
            nonlocal capturedDeserializer
            # Capture the value_deserializer function
            capturedDeserializer = kwargs.get("value_deserializer")

            mockInstance = AsyncMock()
            mockInstance.start = AsyncMock()
            mockInstance.stop = AsyncMock()

            async def EmptyGen():
                return
                yield

            mockInstance.__aiter__ = lambda self: EmptyGen()
            return mockInstance

        mock_aiokafka_consumer.side_effect = CaptureDeserializer

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)

        # Act
        await consumer.Start([])

        # Test the deserializer with valid JSON bytes
        validJsonBytes = b'{"type": "test.event", "version": 1, "payload": {"testField": "value"}}'
        result = capturedDeserializer(validJsonBytes)

        # Assert
        assert result is not None
        assert isinstance(result, dict)
        assert result["type"] == "test.event"
        assert result["version"] == 1
        assert result["payload"]["testField"] == "value"

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaConsumer")
    @pytest.mark.asyncio
    async def test_StartWithMessageProcessing_ShouldCallDeserializerAndProcessMessage(self, mock_aiokafka_consumer):
        """Test that Start processes messages through the deserializer and message handler."""
        # Arrange
        testConfig = self.CreateTestKafkaConfig()
        mockLogger = self.CreateMockLogger()
        mockFactory = self.CreateMockEventFactory()
        mockEvent = TestDomainEvent(aggregateType="TestAggregate", aggregateId="test-123")
        mockFactory.CreateFromData = AsyncMock(return_value=mockEvent)

        # Create mock subscriber
        mockSubscriber = AsyncMock(spec=IEventSubscriber)
        mockSubscriberHandle = AsyncMock()
        mockSubscriber.Handle = mockSubscriberHandle

        # Create mock message
        mockMessage = Mock()
        mockMessage.topic = testConfig.GetTopicName("test.event", 1)
        mockMessage.value = {"type": "test.event", "version": 1, "payload": {"testField": "value"}}

        # Track deserializer calls
        deserializerCalled = False

        def CaptureDeserializer(*args, **kwargs):
            mockInstance = AsyncMock()
            mockInstance.start = AsyncMock()
            mockInstance.stop = AsyncMock()

            async def SingleMessageGen():
                nonlocal deserializerCalled
                deserializerCalled = True
                yield mockMessage

            mockInstance.__aiter__ = lambda self: SingleMessageGen()
            return mockInstance

        mock_aiokafka_consumer.side_effect = CaptureDeserializer

        consumer = KafkaEventConsumer(testConfig, mockFactory, mockLogger)
        consumer.Subscribe(TestDomainEvent, mockSubscriber)

        # Act
        await consumer.Start([])

        # Assert
        assert deserializerCalled
        mockFactory.CreateFromData.assert_called()  # pylint: disable=no-member
        mockSubscriberHandle.assert_called_once_with(mockEvent)  # pylint: disable=no-member
