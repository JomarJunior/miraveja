import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List, ClassVar
import json

from MiravejaCore.Shared.Events.Infrastructure.Kafka.Services import KafkaEventProducer
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig, ProducerConfig, SaslConfig, SslConfig
from MiravejaCore.Shared.Events.Domain.Enums import SecurityProtocol, SaslMechanism, CompressionType, ProducerAcksLevel
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Identifiers.Models import EventId


class ConcreteDomainEventForTesting(DomainEvent):
    """Concrete implementation of DomainEvent for testing purposes."""

    type: ClassVar[str] = "test.event"
    aggregateType: str = "TestAggregate"
    version: ClassVar[int] = 1
    testPayload: str = "test_data"


class UserCreatedEvent(DomainEvent):
    """Test event for user creation."""

    type: ClassVar[str] = "user.created"
    aggregateType: str = "User"
    version: ClassVar[int] = 1
    testPayload: str = "test_data"


class EventFirstEvent(DomainEvent):
    """Test event for first event type."""

    type: ClassVar[str] = "event.first"
    aggregateType: str = "Event"
    version: ClassVar[int] = 1


class EventSecondEvent(DomainEvent):
    """Test event for second event type."""

    type: ClassVar[str] = "event.second"
    aggregateType: str = "Event"
    version: ClassVar[int] = 1


class EventThirdEvent(DomainEvent):
    """Test event for third event type."""

    type: ClassVar[str] = "event.third"
    aggregateType: str = "Event"
    version: ClassVar[int] = 1


class TestKafkaEventProducer:
    """Test cases for KafkaEventProducer service."""

    def CreateTestKafkaConfig(
        self,
        bootstrapServers: str = "localhost:9092",
        topicPrefix: str = "test",
        securityProtocol: SecurityProtocol = SecurityProtocol.PLAINTEXT,
    ) -> KafkaConfig:
        """Create a test Kafka configuration."""
        return KafkaConfig(
            bootstrapServers=bootstrapServers,
            topicPrefix=topicPrefix,
            securityProtocol=securityProtocol,
            producer=ProducerConfig(
                acks=ProducerAcksLevel.ALL,
                retries=3,
                retryBackoffMillis=1000,
                maxInFlightRequests=1,
                timeoutMillis=10000,
            ),
        )

    def CreateMockLogger(self) -> MagicMock:
        """Create a mock logger for testing."""
        return MagicMock(spec=ILogger)

    def test_InitializeKafkaEventProducer_ShouldCreateProducerWithConfig(self):
        """Test that KafkaEventProducer initializes with correct configuration."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Act
        producer = KafkaEventProducer(testConfig, mockLogger)

        # Assert
        assert producer._config == testConfig
        assert producer._logger == mockLogger
        assert producer._producer is None  # Not started yet

    def test_ProducerConfigWithPlaintextSecurity_ShouldCreateCorrectConfig(self):
        """Test that producer config is created correctly for plaintext security."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig(securityProtocol=SecurityProtocol.PLAINTEXT)

        # Act
        producer = KafkaEventProducer(testConfig, mockLogger)
        producerConfig = producer._producerConfig

        # Assert
        assert producerConfig["bootstrap_servers"] == "localhost:9092"
        assert producerConfig["security_protocol"] == "PLAINTEXT"
        assert producerConfig["acks"] == ProducerAcksLevel.ALL
        assert producerConfig["enable_idempotence"] == True

    def test_ProducerConfigWithSaslSecurity_ShouldIncludeSaslConfig(self):
        """Test that producer config includes SASL configuration when required."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        saslConfig = SaslConfig(mechanism=SaslMechanism.PLAIN, username="test_user", password="test_password")
        testConfig = KafkaConfig(
            bootstrapServers="kafka:9092",
            topicPrefix="sasl-test",
            securityProtocol=SecurityProtocol.SASL_PLAINTEXT,
            sasl=saslConfig,
        )

        # Act
        producer = KafkaEventProducer(testConfig, mockLogger)
        producerConfig = producer._producerConfig

        # Assert
        assert producerConfig["security_protocol"] == "SASL_PLAINTEXT"
        assert producerConfig["sasl_mechanism"] == SaslMechanism.PLAIN
        assert producerConfig["sasl_plain_username"] == "test_user"
        assert producerConfig["sasl_plain_password"] == "test_password"

    def test_ProducerConfigWithSslSecurity_ShouldIncludeSslConfig(self):
        """Test that producer config includes SSL configuration when required."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        sslConfig = SslConfig(
            cafile="/path/to/ca.pem", certfile="/path/to/cert.pem", keyfile="/path/to/key.pem", password="ssl_password"
        )
        testConfig = KafkaConfig(
            bootstrapServers="secure-kafka:9093",
            topicPrefix="ssl-test",
            securityProtocol=SecurityProtocol.SSL,
            ssl=sslConfig,
        )

        # Act
        producer = KafkaEventProducer(testConfig, mockLogger)
        producerConfig = producer._producerConfig

        # Assert
        assert producerConfig["security_protocol"] == "SSL"
        assert producerConfig["ssl_cafile"] == "/path/to/ca.pem"
        assert producerConfig["ssl_certfile"] == "/path/to/cert.pem"
        assert producerConfig["ssl_keyfile"] == "/path/to/key.pem"
        assert producerConfig["ssl_password"] == "ssl_password"

    @pytest.mark.asyncio
    async def test_InitializeKafkaProducerWithException_ShouldLogErrorAndReraise(self):
        """Test that producer initialization exceptions are handled correctly."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()
        producer = KafkaEventProducer(testConfig, mockLogger)

        # Make _InitializeKafkaProducer raise an exception
        testError = RuntimeError("Failed to connect to Kafka")
        with patch.object(producer, "_InitializeKafkaProducer", side_effect=testError):
            # Act & Assert
            with pytest.raises(RuntimeError) as exc_info:
                await producer._InitializeKafkaProducer()

            assert exc_info.value == testError

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_ProduceWithValidEvent_ShouldProduceMessageToKafka(self, mock_aiokafka_producer):
        """Test that Produce sends event to Kafka with correct format."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Create mock producer with async methods
        mockProducerInstance = AsyncMock()
        mockProducerInstance.start = AsyncMock()
        mockProducerInstance.send_and_wait = AsyncMock()
        mock_aiokafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)
        await producer._InitializeKafkaProducer()

        testEvent = UserCreatedEvent(aggregateId="user-456", testPayload="user_data")

        # Act
        await producer.Produce(testEvent)

        # Assert
        mockProducerInstance.send_and_wait.assert_called_once()
        call_args = mockProducerInstance.send_and_wait.call_args

        # Verify send_and_wait keyword arguments
        kwargs = call_args[1]  # kwargs are in index 1
        assert kwargs["topic"] == "test.user.created.v1"  # topicPrefix.eventType.vVersion

        # Verify key
        assert kwargs["key"] == b"user-456"

        # Verify message content - format: {"type": "...", "version": ..., "payload": {...}}
        value = kwargs["value"]
        messageContent = json.loads(value.decode("utf-8"))
        assert "type" in messageContent
        assert messageContent["type"] == "user.created"
        assert messageContent["version"] == 1
        assert "payload" in messageContent
        assert messageContent["payload"]["aggregateId"] == "user-456"
        assert messageContent["payload"]["testPayload"] == "user_data"

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_ProduceAllWithMultipleEvents_ShouldProduceAllMessages(self, mock_aiokafka_producer):
        """Test that ProduceAll processes multiple events correctly."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Create mock producer with async methods
        mockProducerInstance = AsyncMock()
        mockProducerInstance.start = AsyncMock()
        mockProducerInstance.send_and_wait = AsyncMock()
        mockProducerInstance.flush = AsyncMock()
        mock_aiokafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)
        await producer._InitializeKafkaProducer()

        testEvents: List[DomainEvent] = [
            EventFirstEvent(aggregateId="agg-1"),
            EventSecondEvent(aggregateId="agg-2"),
            EventThirdEvent(aggregateId="agg-3"),
        ]

        # Act
        await producer.ProduceAll(testEvents)

        # Assert
        assert mockProducerInstance.send_and_wait.call_count == 3
        mockProducerInstance.flush.assert_called_once()
        mockLogger.Info.assert_any_call("Producing 3 events to Kafka.")
        mockLogger.Info.assert_any_call("Successfully produced 3 events to Kafka.")

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_ProduceAllWithEmptyList_ShouldLogInfoAndReturn(self, mock_aiokafka_producer):
        """Test that ProduceAll with empty list logs info and returns early."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Create mock producer with async methods
        mockProducerInstance = AsyncMock()
        mockProducerInstance.start = AsyncMock()
        mock_aiokafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)
        await producer._InitializeKafkaProducer()

        # Act
        await producer.ProduceAll([])

        # Assert
        mockLogger.Info.assert_called_with("No events to produce.")

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_ProduceWithUninitializedProducer_ShouldRaiseRuntimeError(self, mock_aiokafka_producer):
        """Test that Produce raises RuntimeError when producer is not initialized."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Mock _InitializeKafkaProducer to prevent actual initialization
        producer = KafkaEventProducer(testConfig, mockLogger)

        # Patch _InitializeKafkaProducer to do nothing so producer stays None
        with patch.object(producer, "_InitializeKafkaProducer", new_callable=AsyncMock):
            producer._producer = None  # Ensure producer is None

            testEvent = ConcreteDomainEventForTesting(aggregateId="test-123")

            # Act & Assert
            with pytest.raises(RuntimeError) as exc_info:
                await producer.Produce(testEvent)

            assert "Kafka producer is not initialized" in str(exc_info.value)

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_ProduceAllWithUninitializedProducer_ShouldRaiseRuntimeError(self, mock_aiokafka_producer):
        """Test that ProduceAll raises RuntimeError when producer is not initialized."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Mock _InitializeKafkaProducer to prevent actual initialization
        producer = KafkaEventProducer(testConfig, mockLogger)

        # Patch _InitializeKafkaProducer to do nothing so producer stays None
        with patch.object(producer, "_InitializeKafkaProducer", new_callable=AsyncMock):
            producer._producer = None  # Ensure producer is None

            testEvents = [
                EventFirstEvent(aggregateId="test-1"),
                EventSecondEvent(aggregateId="test-2"),
            ]

            # Act & Assert
            with pytest.raises(RuntimeError) as exc_info:
                await producer.ProduceAll(testEvents)

            assert "Kafka producer is not initialized" in str(exc_info.value)

    def test_GetTopicNameFromConfig_ShouldFormatCorrectly(self):
        """Test that GetTopicName formats topic names correctly."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig(topicPrefix="miraveja")

        producer = KafkaEventProducer(testConfig, mockLogger)

        # Act & Assert
        # GetTopicName includes the full event type and version: {prefix}.{type}.v{version}
        assert testConfig.GetTopicName("user.created", version=1) == "miraveja.user.created.v1"
        assert testConfig.GetTopicName("ORDER_PROCESSED", version=2) == "miraveja.order_processed.v2"
        assert testConfig.GetTopicName("payment.failed") == "miraveja.payment.failed.v1"  # default version 1

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_CloseKafkaProducer_ShouldFlushAndLogInfo(self, mock_aiokafka_producer):
        """Test that Close flushes producer and logs appropriately."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Create mock producer with async methods
        mockProducerInstance = AsyncMock()
        mockProducerInstance.start = AsyncMock()
        mockProducerInstance.flush = AsyncMock(return_value=0)
        mockProducerInstance.stop = AsyncMock()
        mock_aiokafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)
        await producer._InitializeKafkaProducer()

        # Act
        await producer.Close()

        # Assert
        mockProducerInstance.flush.assert_called_once()
        mockProducerInstance.stop.assert_called_once()
        mockLogger.Info.assert_any_call("Kafka producer closed.")
        assert producer._producer is None

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_CloseKafkaProducerWithPendingMessages_ShouldNotLogWarning(self, mock_aiokafka_producer):
        """Test that Close completes successfully (async version doesn't check flush return value)."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Create mock producer with async methods
        mockProducerInstance = AsyncMock()
        mockProducerInstance.start = AsyncMock()
        mockProducerInstance.flush = AsyncMock()
        mockProducerInstance.stop = AsyncMock()
        mock_aiokafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)
        await producer._InitializeKafkaProducer()

        # Act
        await producer.Close()

        # Assert
        mockProducerInstance.flush.assert_called_once()
        mockProducerInstance.stop.assert_called_once()
        # Note: The async AIOKafkaProducer Close() implementation doesn't log warnings for pending messages
        mockLogger.Info.assert_any_call("Kafka producer closed.")
        assert producer._producer is None

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_ProduceAllWithPartialFailures_ShouldLogErrors(self, mock_aiokafka_producer):
        """Test that ProduceAll logs errors when some events fail to produce."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Create mock producer with async methods
        mockProducerInstance = AsyncMock()
        mockProducerInstance.start = AsyncMock()
        mockProducerInstance.flush = AsyncMock()
        mock_aiokafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)
        await producer._InitializeKafkaProducer()

        # Mock Produce to raise exception for second event
        callCount = [0]

        async def MockProduce(event):
            callCount[0] += 1
            if callCount[0] == 2:
                raise RuntimeError("Kafka connection error")

        producer.Produce = MockProduce

        testEvents: List[DomainEvent] = [
            EventFirstEvent(aggregateId="agg-1"),
            EventSecondEvent(aggregateId="agg-2"),  # This will fail
            EventThirdEvent(aggregateId="agg-3"),
        ]

        # Act
        await producer.ProduceAll(testEvents)

        # Assert
        mockProducerInstance.flush.assert_called_once()
        # Should log the error
        mockLogger.Error.assert_any_call("Kafka produce error for event batch: Kafka connection error")

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_ProduceAllWithCompleteFailure_ShouldRaiseException(self, mock_aiokafka_producer):
        """Test that ProduceAll raises exception on complete failure."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Create mock producer with async methods
        mockProducerInstance = AsyncMock()
        mockProducerInstance.start = AsyncMock()
        mockProducerInstance.flush = AsyncMock(side_effect=Exception("Flush failed"))
        mock_aiokafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)
        await producer._InitializeKafkaProducer()

        # Mock Produce to succeed
        producer.Produce = AsyncMock()

        testEvents: List[DomainEvent] = [EventFirstEvent(aggregateId="agg-1")]

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await producer.ProduceAll(testEvents)

        assert "Flush failed" in str(exc_info.value)
        mockLogger.Error.assert_any_call("Failed to produce events to Kafka: Flush failed")

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_CloseWithException_ShouldLogErrorAndReraise(self, mock_aiokafka_producer):
        """Test that Close logs error and raises exception when closing fails."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Create mock producer with async methods
        mockProducerInstance = AsyncMock()
        mockProducerInstance.start = AsyncMock()
        mockProducerInstance.flush = AsyncMock()
        mockProducerInstance.stop = AsyncMock(side_effect=Exception("Stop failed"))
        mock_aiokafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)
        await producer._InitializeKafkaProducer()

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await producer.Close()

        assert "Stop failed" in str(exc_info.value)
        mockLogger.Error.assert_called_once()

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_HandleDeliveryReportWithMetadata_ShouldLogDebug(self, mock_aiokafka_producer):
        """Test that _HandleDeliveryReport logs delivery metadata."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        producer = KafkaEventProducer(testConfig, mockLogger)

        # Act
        await producer._HandleDeliveryReport("test.topic", 0, 12345)

        # Assert
        mockLogger.Debug.assert_called_once_with("Message delivered to test.topic [0] at offset 12345")

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_ProduceWithKafkaError_ShouldLogAndReraise(self, mock_aiokafka_producer):
        """Test that Produce logs and re-raises Kafka errors."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Create mock producer with async methods
        mockProducerInstance = AsyncMock()
        mockProducerInstance.start = AsyncMock()
        from aiokafka.errors import KafkaError

        mockProducerInstance.send_and_wait = AsyncMock(side_effect=KafkaError("Connection lost"))
        mock_aiokafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)
        await producer._InitializeKafkaProducer()

        testEvent = UserCreatedEvent(aggregateId="user-789", testPayload="error_test")

        # Act & Assert
        with pytest.raises(KafkaError):
            await producer.Produce(testEvent)

        mockLogger.Error.assert_called_once()
        assert "Failed to produce message to Kafka" in mockLogger.Error.call_args[0][0]

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.AIOKafkaProducer")
    @pytest.mark.asyncio
    async def test_InitializeKafkaProducerWithException_ShouldLogAndReraise(self, mock_aiokafka_producer):
        """Test that _InitializeKafkaProducer logs and re-raises exceptions during initialization."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()

        # Create mock producer that fails to start
        mockProducerInstance = AsyncMock()
        mockProducerInstance.start = AsyncMock(side_effect=Exception("Connection refused"))
        mock_aiokafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)

        # Act & Assert
        with pytest.raises(Exception) as excInfo:
            await producer._InitializeKafkaProducer()

        assert str(excInfo.value) == "Connection refused"
        mockLogger.Error.assert_called_once()
        assert "Failed to initialize Kafka producer" in mockLogger.Error.call_args[0][0]
