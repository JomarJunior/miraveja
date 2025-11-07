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

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    def test_InitializeKafkaEventProducer_ShouldCreateProducerWithConfig(self, mock_kafka_producer):
        """Test that KafkaEventProducer initializes with correct configuration."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()
        mockProducerInstance = MagicMock()
        mock_kafka_producer.return_value = mockProducerInstance

        # Act
        producer = KafkaEventProducer(testConfig, mockLogger)

        # Assert
        mock_kafka_producer.assert_called_once()
        mockLogger.Info.assert_called_with("Kafka producer initialized successfully.")
        assert producer._config == testConfig
        assert producer._logger == mockLogger

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    def test_ProducerConfigWithPlaintextSecurity_ShouldCreateCorrectConfig(self, mock_kafka_producer):
        """Test that producer config is created correctly for plaintext security."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig(securityProtocol=SecurityProtocol.PLAINTEXT)
        mockProducerInstance = MagicMock()
        mock_kafka_producer.return_value = mockProducerInstance

        # Act
        producer = KafkaEventProducer(testConfig, mockLogger)

        # Assert
        call_args = mock_kafka_producer.call_args[0][0]
        assert call_args["bootstrap.servers"] == "localhost:9092"
        assert call_args["security.protocol"] == "PLAINTEXT"
        assert call_args["acks"] == "all"
        assert call_args["retries"] == 3
        assert call_args["enable.idempotence"] == True

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    def test_ProducerConfigWithSaslSecurity_ShouldIncludeSaslConfig(self, mock_kafka_producer):
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
        mockProducerInstance = MagicMock()
        mock_kafka_producer.return_value = mockProducerInstance

        # Act
        producer = KafkaEventProducer(testConfig, mockLogger)

        # Assert
        call_args = mock_kafka_producer.call_args[0][0]
        assert call_args["security.protocol"] == "SASL_PLAINTEXT"
        assert call_args["sasl.mechanism"] == "PLAIN"
        assert call_args["sasl.username"] == "test_user"
        assert call_args["sasl.password"] == "test_password"

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    def test_ProducerConfigWithSslSecurity_ShouldIncludeSslConfig(self, mock_kafka_producer):
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
        mockProducerInstance = MagicMock()
        mock_kafka_producer.return_value = mockProducerInstance

        # Act
        producer = KafkaEventProducer(testConfig, mockLogger)

        # Assert
        call_args = mock_kafka_producer.call_args[0][0]
        assert call_args["security.protocol"] == "SSL"
        assert call_args["ssl.ca.location"] == "/path/to/ca.pem"
        assert call_args["ssl.certificate.location"] == "/path/to/cert.pem"
        assert call_args["ssl.key.location"] == "/path/to/key.pem"
        assert call_args["ssl.key.password"] == "ssl_password"

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    def test_InitializeKafkaProducerWithException_ShouldLogErrorAndReraise(self, mock_kafka_producer):
        """Test that producer initialization exceptions are handled correctly."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()
        testError = RuntimeError("Failed to connect to Kafka")
        mock_kafka_producer.side_effect = testError

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            KafkaEventProducer(testConfig, mockLogger)

        assert exc_info.value == testError
        mockLogger.Error.assert_called_with(f"Failed to initialize Kafka producer: {testError}")

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    @patch("asyncio.to_thread")
    @pytest.mark.asyncio
    async def test_ProduceWithValidEvent_ShouldProduceMessageToKafka(self, mock_to_thread, mock_kafka_producer):
        """Test that Produce sends event to Kafka with correct format."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()
        mockProducerInstance = MagicMock()
        mock_kafka_producer.return_value = mockProducerInstance
        mock_to_thread.return_value = None

        producer = KafkaEventProducer(testConfig, mockLogger)
        testEvent = UserCreatedEvent(aggregateId="user-456", testPayload="user_data")

        # Act
        await producer.Produce(testEvent)

        # Assert
        mock_to_thread.assert_called_once()
        call_args = mock_to_thread.call_args
        assert call_args[0][0] == mockProducerInstance.produce

        # Verify produce call arguments
        kwargs = call_args[1]
        assert kwargs["topic"] == "test.user"  # GetTopicName extracts first part: "user"
        assert kwargs["key"] == b"user-456"

        # Verify message content - new format: {"class": "...", "payload": {...}}
        messageContent = json.loads(kwargs["value"].decode("utf-8"))
        assert "class" in messageContent
        assert messageContent["class"].endswith("UserCreatedEvent")
        assert "payload" in messageContent
        assert messageContent["payload"]["aggregateId"] == "user-456"
        assert messageContent["payload"]["testPayload"] == "user_data"

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    @patch("asyncio.to_thread")
    @pytest.mark.asyncio
    async def test_ProduceAllWithMultipleEvents_ShouldProduceAllMessages(self, mock_to_thread, mock_kafka_producer):
        """Test that ProduceAll processes multiple events correctly."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()
        mockProducerInstance = MagicMock()
        mock_kafka_producer.return_value = mockProducerInstance
        mock_to_thread.return_value = None

        producer = KafkaEventProducer(testConfig, mockLogger)
        testEvents: List[DomainEvent] = [
            EventFirstEvent(aggregateId="agg-1"),
            EventSecondEvent(aggregateId="agg-2"),
            EventThirdEvent(aggregateId="agg-3"),
        ]

        # Configure the mock to return 0 for flush (no remaining messages)
        mock_to_thread.return_value = 0

        # Act
        await producer.ProduceAll(testEvents)

        # Assert
        # Should call to_thread for each event plus flush
        assert mock_to_thread.call_count >= 2  # flush operation (poll is not called separately)
        mockLogger.Info.assert_any_call("Producing 3 events to Kafka.")
        mockLogger.Info.assert_any_call("Successfully produced 3 events to Kafka.")

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    @pytest.mark.asyncio
    async def test_ProduceAllWithEmptyList_ShouldLogInfoAndReturn(self, mock_kafka_producer):
        """Test that ProduceAll with empty list logs info and returns early."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()
        mockProducerInstance = MagicMock()
        mock_kafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)

        # Act
        await producer.ProduceAll([])

        # Assert
        mockLogger.Info.assert_called_with("No events to produce.")

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    @pytest.mark.asyncio
    async def test_ProduceWithUninitializedProducer_ShouldRaiseRuntimeError(self, mock_kafka_producer):
        """Test that Produce raises RuntimeError when producer is not initialized."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()
        mockProducerInstance = MagicMock()
        mock_kafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)
        producer._producer = None  # Simulate uninitialized producer

        testEvent = ConcreteDomainEventForTesting(aggregateId="test-123")

        # Act & Assert
        with pytest.raises(RuntimeError) as exc_info:
            await producer.Produce(testEvent)

        assert "Kafka producer is not initialized" in str(exc_info.value)

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    def test_GetTopicNameFromConfig_ShouldFormatCorrectly(self, mock_kafka_producer):
        """Test that GetTopicName formats topic names correctly."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig(topicPrefix="miraveja")
        mockProducerInstance = MagicMock()
        mock_kafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)

        # Act & Assert
        # GetTopicName extracts only the first part before the dot (if dot exists)
        assert testConfig.GetTopicName("user.created") == "miraveja.user"
        assert testConfig.GetTopicName("ORDER_PROCESSED") == "miraveja.order_processed"  # No dot, keeps all
        assert testConfig.GetTopicName("payment.failed") == "miraveja.payment"  # Has dot, first part

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    def test_CloseKafkaProducer_ShouldFlushAndLogInfo(self, mock_kafka_producer):
        """Test that Close flushes producer and logs appropriately."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()
        mockProducerInstance = MagicMock()
        mockProducerInstance.flush.return_value = 0
        mock_kafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)

        # Act
        producer.Close()

        # Assert
        mockProducerInstance.flush.assert_called_once_with(timeout=10.0)
        mockLogger.Info.assert_any_call("All messages successfully delivered before closing Kafka producer.")
        mockLogger.Info.assert_any_call("Kafka producer closed.")
        assert producer._producer is None

    @patch("MiravejaCore.Shared.Events.Infrastructure.Kafka.Services.KafkaProducer")
    def test_CloseKafkaProducerWithPendingMessages_ShouldLogWarning(self, mock_kafka_producer):
        """Test that Close logs warning when messages are still pending."""
        # Arrange
        mockLogger = self.CreateMockLogger()
        testConfig = self.CreateTestKafkaConfig()
        mockProducerInstance = MagicMock()
        mockProducerInstance.flush.return_value = 5  # 5 pending messages
        mock_kafka_producer.return_value = mockProducerInstance

        producer = KafkaEventProducer(testConfig, mockLogger)

        # Act
        producer.Close()

        # Assert
        mockProducerInstance.flush.assert_called_once_with(timeout=10.0)
        mockLogger.Warning.assert_called_with("Kafka producer closed with 5 messages still pending delivery.")
        mockLogger.Info.assert_any_call("Kafka producer closed.")
        assert producer._producer is None
