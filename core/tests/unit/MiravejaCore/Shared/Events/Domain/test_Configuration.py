import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError

from MiravejaCore.Shared.Events.Domain.Configuration import (
    KafkaConfig,
    ProducerConfig,
    ConsumerConfig,
    SaslConfig,
    SslConfig,
)
from MiravejaCore.Shared.Events.Domain.Enums import (
    SecurityProtocol,
    SaslMechanism,
    CompressionType,
    ProducerAcksLevel,
    ConsumerAutoOffsetReset,
)
from MiravejaCore.Shared.Utils.Constants.Time import MILLIS_1_SEC, MILLIS_10_SEC


class TestProducerConfig:
    """Test cases for ProducerConfig model."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that ProducerConfig initializes with correct default values."""
        # Act
        config = ProducerConfig()

        # Assert
        assert config.acks == ProducerAcksLevel.ALL
        assert config.retries == 3
        assert config.retryBackoffMillis == 1000
        assert config.maxInFlightRequests == 1
        assert config.timeoutMillis == 10000

    def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
        """Test that ProducerConfig initializes with custom values correctly."""
        # Act
        config = ProducerConfig(
            acks=ProducerAcksLevel.LEADER,
            retries=5,
            retryBackoffMillis=2000,
            maxInFlightRequests=3,
            timeoutMillis=15000,
        )

        # Assert
        assert config.acks == ProducerAcksLevel.LEADER
        assert config.retries == 5
        assert config.retryBackoffMillis == 2000
        assert config.maxInFlightRequests == 3
        assert config.timeoutMillis == 15000

    @patch.dict(
        os.environ,
        {
            "KAFKA_PRODUCER_ACKS": "1",
            "KAFKA_PRODUCER_RETRIES": "7",
            "KAFKA_PRODUCER_RETRY_BACKOFF_MILLIS": "3000",
            "KAFKA_PRODUCER_MAX_IN_FLIGHT_REQUESTS": "5",
            "KAFKA_PRODUCER_TIMEOUT_MILLIS": "20000",
        },
    )
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
        """Test that ProducerConfig.FromEnv creates instance from environment variables."""
        # Act
        config = ProducerConfig.FromEnv()

        # Assert
        assert config.acks == ProducerAcksLevel.LEADER
        assert config.retries == 7
        assert config.retryBackoffMillis == 3000
        assert config.maxInFlightRequests == 5
        assert config.timeoutMillis == 20000

    @patch.dict(os.environ, {}, clear=True)
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(self):
        """Test that ProducerConfig.FromEnv uses default values when environment variables are not set."""
        # Act
        config = ProducerConfig.FromEnv()

        # Assert - Should use defaults from the class definition
        assert config.acks == ProducerAcksLevel.ALL
        assert config.retries == 3
        assert config.retryBackoffMillis == MILLIS_1_SEC
        assert config.maxInFlightRequests == 1
        assert config.timeoutMillis == MILLIS_10_SEC


class TestConsumerConfig:
    """Test cases for ConsumerConfig model."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that ConsumerConfig initializes with correct default values."""
        # Act
        config = ConsumerConfig()

        # Assert
        assert config.groupId == "miraveja-group"
        assert config.autoOffsetReset == ConsumerAutoOffsetReset.EARLIEST
        assert config.enableAutoCommit == True
        assert config.autoCommitIntervalMillis == 5000
        assert config.sessionTimeoutMillis == 10000
        assert config.heartbeatIntervalMillis == 3000

    def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
        """Test that ConsumerConfig initializes with custom values correctly."""
        # Act
        config = ConsumerConfig(
            groupId="custom-group",
            autoOffsetReset=ConsumerAutoOffsetReset.LATEST,
            enableAutoCommit=False,
            autoCommitIntervalMillis=2000,
            sessionTimeoutMillis=15000,
            heartbeatIntervalMillis=4000,
        )

        # Assert
        assert config.groupId == "custom-group"
        assert config.autoOffsetReset == ConsumerAutoOffsetReset.LATEST
        assert config.enableAutoCommit == False
        assert config.autoCommitIntervalMillis == 2000
        assert config.sessionTimeoutMillis == 15000
        assert config.heartbeatIntervalMillis == 4000

    @patch.dict(
        os.environ,
        {
            "KAFKA_CONSUMER_GROUP_ID": "env-group",
            "KAFKA_CONSUMER_AUTO_OFFSET_RESET": "latest",
            "KAFKA_CONSUMER_ENABLE_AUTO_COMMIT": "false",
            "KAFKA_CONSUMER_AUTO_COMMIT_INTERVAL_MILLIS": "3000",
            "KAFKA_CONSUMER_SESSION_TIMEOUT_MILLIS": "12000",
            "KAFKA_CONSUMER_HEARTBEAT_INTERVAL_MILLIS": "2500",
        },
    )
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
        """Test that ConsumerConfig.FromEnv creates instance from environment variables."""
        # Act
        config = ConsumerConfig.FromEnv()

        # Assert
        assert config.groupId == "env-group"
        assert config.autoOffsetReset == ConsumerAutoOffsetReset.LATEST
        assert config.enableAutoCommit == False
        assert config.autoCommitIntervalMillis == 3000
        assert config.sessionTimeoutMillis == 12000
        assert config.heartbeatIntervalMillis == 2500


class TestSaslConfig:
    """Test cases for SaslConfig model."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that SaslConfig initializes with correct default values."""
        # Act
        config = SaslConfig()

        # Assert
        assert config.mechanism == SaslMechanism.PLAIN
        assert config.username == ""
        assert config.password == ""

    def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
        """Test that SaslConfig initializes with custom values correctly."""
        # Act
        config = SaslConfig(mechanism=SaslMechanism.SCRAM_SHA_256, username="test_user", password="test_password")

        # Assert
        assert config.mechanism == SaslMechanism.SCRAM_SHA_256
        assert config.username == "test_user"
        assert config.password == "test_password"

    @patch.dict(
        os.environ,
        {
            "KAFKA_SASL_MECHANISM": "SCRAM-SHA-512",
            "KAFKA_SASL_USERNAME": "sasl_user",
            "KAFKA_SASL_PASSWORD": "sasl_secret",
        },
    )
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
        """Test that SaslConfig.FromEnv creates instance from environment variables."""
        # Act
        config = SaslConfig.FromEnv()

        # Assert
        assert config.mechanism == SaslMechanism.SCRAM_SHA_512
        assert config.username == "sasl_user"
        assert config.password == "sasl_secret"


class TestSslConfig:
    """Test cases for SslConfig model."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that SslConfig initializes with correct default values."""
        # Act
        config = SslConfig()

        # Assert
        assert config.cafile == ""
        assert config.certfile == ""
        assert config.keyfile == ""
        assert config.password == ""

    def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
        """Test that SslConfig initializes with custom values correctly."""
        # Act
        config = SslConfig(
            cafile="/path/to/ca.pem", certfile="/path/to/cert.pem", keyfile="/path/to/key.pem", password="ssl_password"
        )

        # Assert
        assert config.cafile == "/path/to/ca.pem"
        assert config.certfile == "/path/to/cert.pem"
        assert config.keyfile == "/path/to/key.pem"
        assert config.password == "ssl_password"

    @patch.dict(
        os.environ,
        {
            "KAFKA_SSL_CAFILE": "/env/ca.crt",
            "KAFKA_SSL_CERTFILE": "/env/client.crt",
            "KAFKA_SSL_KEYFILE": "/env/client.key",
            "KAFKA_SSL_PASSWORD": "env_ssl_pass",
        },
    )
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
        """Test that SslConfig.FromEnv creates instance from environment variables."""
        # Act
        config = SslConfig.FromEnv()

        # Assert
        assert config.cafile == "/env/ca.crt"
        assert config.certfile == "/env/client.crt"
        assert config.keyfile == "/env/client.key"
        assert config.password == "env_ssl_pass"


class TestKafkaConfig:
    """Test cases for KafkaConfig model."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that KafkaConfig initializes with correct default values."""
        # Act
        config = KafkaConfig()

        # Assert
        assert config.bootstrapServers == "localhost:9092"
        assert config.topicPrefix == "miraveja"
        assert isinstance(config.producer, ProducerConfig)
        assert isinstance(config.consumer, ConsumerConfig)
        assert config.securityProtocol == SecurityProtocol.PLAINTEXT
        assert config.sasl is None
        assert config.ssl is None
        assert config.enableIdempotence == True
        assert config.compressionType == CompressionType.GZIP
        assert config.batchSize == 16 * 1024 * 1024  # 16MB
        assert config.lingerMillis == 5
        assert config.bufferMemory == 32 * 1024 * 1024  # 32MB

    def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
        """Test that KafkaConfig initializes with custom values correctly."""
        # Arrange
        customProducer = ProducerConfig(retries=10)
        customConsumer = ConsumerConfig(groupId="custom-group")
        customSasl = SaslConfig(username="user")
        customSsl = SslConfig(cafile="/ca.pem")

        # Act
        config = KafkaConfig(
            bootstrapServers="kafka1:9092,kafka2:9092",
            topicPrefix="custom",
            producer=customProducer,
            consumer=customConsumer,
            securityProtocol=SecurityProtocol.SASL_SSL,
            sasl=customSasl,
            ssl=customSsl,
            enableIdempotence=False,
            compressionType=CompressionType.SNAPPY,
            batchSize=8 * 1024 * 1024,
            lingerMillis=10,
            bufferMemory=64 * 1024 * 1024,
        )

        # Assert
        assert config.bootstrapServers == "kafka1:9092,kafka2:9092"
        assert config.topicPrefix == "custom"
        assert config.producer == customProducer
        assert config.consumer == customConsumer
        assert config.securityProtocol == SecurityProtocol.SASL_SSL
        assert config.sasl == customSasl
        assert config.ssl == customSsl
        assert config.enableIdempotence == False
        assert config.compressionType == CompressionType.SNAPPY
        assert config.batchSize == 8 * 1024 * 1024
        assert config.lingerMillis == 10
        assert config.bufferMemory == 64 * 1024 * 1024

    @patch.dict(
        os.environ,
        {
            "KAFKA_BOOTSTRAP_SERVERS": "prod-kafka:9092",
            "KAFKA_TOPIC_PREFIX": "production",
            "KAFKA_SECURITY_PROTOCOL": "SASL_SSL",
            "KAFKA_SASL_MECHANISM": "SCRAM-SHA-256",
            "KAFKA_SASL_USERNAME": "prod_user",
            "KAFKA_SASL_PASSWORD": "prod_password",  # Added missing password
            "KAFKA_SSL_CAFILE": "/prod/ca.pem",
            "KAFKA_SSL_CERTFILE": "/prod/client.crt",
            "KAFKA_SSL_KEYFILE": "/prod/client.key",
            "KAFKA_ENABLE_IDEMPOTENCE": "false",
            "KAFKA_COMPRESSION_TYPE": "lz4",
            "KAFKA_BATCH_SIZE": "8388608",  # 8MB
            "KAFKA_LINGER_MILLIS": "20",
            "KAFKA_BUFFER_MEMORY": "67108864",  # 64MB
            # Add all required producer config env vars
            "KAFKA_PRODUCER_ACKS": "all",
            "KAFKA_PRODUCER_RETRIES": "3",
            "KAFKA_PRODUCER_RETRY_BACKOFF_MILLIS": "1000",
            "KAFKA_PRODUCER_MAX_IN_FLIGHT_REQUESTS": "1",
            "KAFKA_PRODUCER_TIMEOUT_MILLIS": "10000",
            # Add all required consumer config env vars
            "KAFKA_CONSUMER_GROUP_ID": "prod-group",
            "KAFKA_CONSUMER_AUTO_OFFSET_RESET": "earliest",
            "KAFKA_CONSUMER_ENABLE_AUTO_COMMIT": "true",
            "KAFKA_CONSUMER_AUTO_COMMIT_INTERVAL_MILLIS": "5000",
            "KAFKA_CONSUMER_SESSION_TIMEOUT_MILLIS": "10000",
            "KAFKA_CONSUMER_HEARTBEAT_INTERVAL_MILLIS": "3000",
        },
    )
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
        """Test that KafkaConfig.FromEnv creates instance from environment variables."""
        # Act
        config = KafkaConfig.FromEnv()

        # Assert
        assert config.bootstrapServers == "prod-kafka:9092"
        assert config.topicPrefix == "production"
        assert config.securityProtocol == SecurityProtocol.SASL_SSL
        assert config.sasl is not None
        assert config.sasl.mechanism == SaslMechanism.SCRAM_SHA_256
        assert config.sasl.username == "prod_user"
        assert config.sasl.password == "prod_password"
        assert config.ssl is not None
        assert config.ssl.cafile == "/prod/ca.pem"
        assert config.enableIdempotence == False
        assert config.compressionType == CompressionType.LZ4
        assert config.batchSize == 8388608
        assert config.lingerMillis == 20
        assert config.bufferMemory == 67108864

    @patch.dict(os.environ, {"KAFKA_BOOTSTRAP_SERVERS": "simple-kafka:9092"}, clear=True)
    def test_FromEnvWithPartialEnvironmentVariables_ShouldUseDefaults(self):
        """Test that KafkaConfig.FromEnv uses defaults for missing environment variables."""
        # Act
        config = KafkaConfig.FromEnv()

        # Assert - Should use the provided bootstrap servers and defaults for the rest
        assert config.bootstrapServers == "simple-kafka:9092"
        assert config.topicPrefix == "miraveja"  # default
        assert config.producer is not None
        assert config.consumer is not None
        assert config.securityProtocol == SecurityProtocol.PLAINTEXT  # default
        assert config.sasl is None  # no SASL env vars set
        assert config.ssl is None  # no SSL env vars set

    def test_GetTopicNameWithSimpleEventType_ShouldFormatCorrectly(self):
        """Test that GetTopicName formats topic name with prefix, event type, and version."""
        # Arrange
        config = KafkaConfig(topicPrefix="test")

        # Act & Assert
        # GetTopicName now includes version suffix
        assert config.GetTopicName("user.created") == "test.user.created.v1"
        assert config.GetTopicName("order.processed") == "test.order.processed.v1"
        assert config.GetTopicName("payment.failed") == "test.payment.failed.v1"

    def test_GetTopicNameWithUnderscoreEventType_ShouldConvertToLowercase(self):
        """Test that GetTopicName converts event types with underscores to lowercase."""
        # Arrange
        config = KafkaConfig(topicPrefix="miraveja")

        # Act & Assert
        # Converts to lowercase and adds version suffix
        assert config.GetTopicName("user_profile_updated") == "miraveja.user_profile_updated.v1"
        assert config.GetTopicName("ORDER_STATUS_CHANGED") == "miraveja.order_status_changed.v1"
        assert config.GetTopicName("payment_method_added") == "miraveja.payment_method_added.v1"

    def test_GetTopicNameWithMixedCaseEventType_ShouldConvertToLowercase(self):
        """Test that GetTopicName converts event types to lowercase with version."""
        # Arrange
        config = KafkaConfig(topicPrefix="events")

        # Act & Assert
        assert config.GetTopicName("UserRegistered") == "events.userregistered.v1"
        assert config.GetTopicName("ORDER.COMPLETED") == "events.order.completed.v1"
        assert config.GetTopicName("Payment_Failed") == "events.payment_failed.v1"

    @patch("builtins.open")
    @patch("json.load")
    def test_FromJsonFileWithValidFile_ShouldReturnConfig(self, mock_json_load, mock_open):
        """Test that KafkaConfig.FromJsonFile creates config from JSON file."""
        # Arrange
        mock_json_data = {"bootstrapServers": "json-kafka:9092", "topicPrefix": "json-test", "securityProtocol": "SSL"}
        mock_json_load.return_value = mock_json_data
        mock_file = mock_open.return_value.__enter__.return_value

        # Act
        config = KafkaConfig.FromJsonFile("/path/to/config.json")

        # Assert
        mock_open.assert_called_once_with("/path/to/config.json", "r", encoding="utf-8")
        mock_json_load.assert_called_once_with(mock_file)
        assert config.bootstrapServers == "json-kafka:9092"
        assert config.topicPrefix == "json-test"
        assert config.securityProtocol == SecurityProtocol.SSL

    def test_GetTopicNameWithCustomVersion_ShouldIncludeVersion(self):
        """Test that GetTopicName includes custom version in topic name."""
        # Arrange
        config = KafkaConfig(topicPrefix="versioned")

        # Act & Assert
        assert config.GetTopicName("user.created", version=1) == "versioned.user.created.v1"
        assert config.GetTopicName("user.created", version=2) == "versioned.user.created.v2"
        assert config.GetTopicName("order.placed", version=5) == "versioned.order.placed.v5"

    def test_GetEventTypeFromTopicWithValidTopic_ShouldExtractEventType(self):
        """Test that GetEventTypeFromTopic extracts event type from valid topic name."""
        # Arrange
        config = KafkaConfig(topicPrefix="miraveja")

        # Act & Assert
        assert config.GetEventTypeFromTopic("miraveja.user.created.v1") == "usercreated"
        assert config.GetEventTypeFromTopic("miraveja.order.placed.v1") == "orderplaced"
        assert config.GetEventTypeFromTopic("miraveja.payment.failed.v1") == "paymentfailed"

    def test_GetEventTypeFromTopicWithCustomVersion_ShouldExtractEventType(self):
        """Test that GetEventTypeFromTopic extracts event type with custom version."""
        # Arrange
        config = KafkaConfig(topicPrefix="events")

        # Act & Assert
        assert config.GetEventTypeFromTopic("events.user.registered.v2", version=2) == "userregistered"
        assert config.GetEventTypeFromTopic("events.order.completed.v3", version=3) == "ordercompleted"
        assert config.GetEventTypeFromTopic("events.payment.processed.v5", version=5) == "paymentprocessed"

    def test_GetEventTypeFromTopicWithInvalidTopic_ShouldReturnOriginal(self):
        """Test that GetEventTypeFromTopic returns original topic name when format is invalid."""
        # Arrange
        config = KafkaConfig(topicPrefix="miraveja")

        # Act & Assert
        assert config.GetEventTypeFromTopic("invalid-topic") == "invalid-topic"
        assert config.GetEventTypeFromTopic("other.prefix.event.v1") == "other.prefix.event.v1"
        assert config.GetEventTypeFromTopic("miraveja.event") == "miraveja.event"
        assert config.GetEventTypeFromTopic("miraveja.event.v2", version=1) == "miraveja.event.v2"

    def test_GetEventTypeFromTopicWithDifferentPrefix_ShouldReturnOriginal(self):
        """Test that GetEventTypeFromTopic returns original when prefix doesn't match."""
        # Arrange
        config = KafkaConfig(topicPrefix="custom")

        # Act & Assert
        assert config.GetEventTypeFromTopic("miraveja.user.created.v1") == "miraveja.user.created.v1"
        assert config.GetEventTypeFromTopic("other.order.placed.v1") == "other.order.placed.v1"


class TestProducerConfigEdgeCases:
    """Test edge cases for ProducerConfig model."""

    def test_InitializeWithZeroRetries_ShouldSetZero(self):
        """Test that ProducerConfig accepts zero retries."""
        # Act
        config = ProducerConfig(retries=0)

        # Assert
        assert config.retries == 0

    def test_InitializeWithLargeTimeout_ShouldSetValue(self):
        """Test that ProducerConfig accepts large timeout values."""
        # Act
        config = ProducerConfig(timeoutMillis=60000)  # 60 seconds

        # Assert
        assert config.timeoutMillis == 60000

    @patch.dict(os.environ, {"KAFKA_PRODUCER_ACKS": "0"})
    def test_FromEnvWithZeroAcks_ShouldSetNone(self):
        """Test that ProducerConfig.FromEnv handles zero acknowledgments."""
        # Act
        config = ProducerConfig.FromEnv()

        # Assert
        assert config.acks == ProducerAcksLevel.NONE

    @patch.dict(os.environ, {"KAFKA_PRODUCER_RETRIES": "0"})
    def test_FromEnvWithZeroRetries_ShouldSetZero(self):
        """Test that ProducerConfig.FromEnv handles zero retries."""
        # Act
        config = ProducerConfig.FromEnv()

        # Assert
        assert config.retries == 0


class TestConsumerConfigEdgeCases:
    """Test edge cases for ConsumerConfig model."""

    @patch.dict(os.environ, {"KAFKA_CONSUMER_ENABLE_AUTO_COMMIT": "true"})
    def test_FromEnvWithTrueAutoCommit_ShouldSetTrue(self):
        """Test that ConsumerConfig.FromEnv handles 'true' string for boolean."""
        # Act
        config = ConsumerConfig.FromEnv()

        # Assert
        assert config.enableAutoCommit == True

    @patch.dict(os.environ, {"KAFKA_CONSUMER_ENABLE_AUTO_COMMIT": "1"})
    def test_FromEnvWithOneAutoCommit_ShouldSetTrue(self):
        """Test that ConsumerConfig.FromEnv handles '1' string for boolean."""
        # Act
        config = ConsumerConfig.FromEnv()

        # Assert
        assert config.enableAutoCommit == True

    @patch.dict(os.environ, {"KAFKA_CONSUMER_ENABLE_AUTO_COMMIT": "yes"})
    def test_FromEnvWithYesAutoCommit_ShouldSetTrue(self):
        """Test that ConsumerConfig.FromEnv handles 'yes' string for boolean."""
        # Act
        config = ConsumerConfig.FromEnv()

        # Assert
        assert config.enableAutoCommit == True

    @patch.dict(os.environ, {"KAFKA_CONSUMER_ENABLE_AUTO_COMMIT": "FALSE"})
    def test_FromEnvWithFalseAutoCommit_ShouldSetFalse(self):
        """Test that ConsumerConfig.FromEnv handles 'FALSE' string for boolean."""
        # Act
        config = ConsumerConfig.FromEnv()

        # Assert
        assert config.enableAutoCommit == False

    @patch.dict(os.environ, {"KAFKA_CONSUMER_ENABLE_AUTO_COMMIT": "0"})
    def test_FromEnvWithZeroAutoCommit_ShouldSetFalse(self):
        """Test that ConsumerConfig.FromEnv handles '0' string for boolean."""
        # Act
        config = ConsumerConfig.FromEnv()

        # Assert
        assert config.enableAutoCommit == False

    def test_InitializeWithCustomGroupId_ShouldSetValue(self):
        """Test that ConsumerConfig accepts custom group IDs."""
        # Act
        config = ConsumerConfig(groupId="my-custom-group-123")

        # Assert
        assert config.groupId == "my-custom-group-123"

    @patch.dict(os.environ, {}, clear=True)
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(self):
        """Test that ConsumerConfig.FromEnv uses default values when no environment variables are set."""
        # Act
        config = ConsumerConfig.FromEnv()

        # Assert
        assert config.groupId == "miraveja-group"
        assert config.autoOffsetReset == ConsumerAutoOffsetReset.EARLIEST
        assert config.enableAutoCommit == True


class TestSaslConfigEdgeCases:
    """Test edge cases for SaslConfig model."""

    def test_InitializeWithEmptyCredentials_ShouldSetEmpty(self):
        """Test that SaslConfig accepts empty credentials."""
        # Act
        config = SaslConfig(username="", password="")

        # Assert
        assert config.username == ""
        assert config.password == ""

    @patch.dict(os.environ, {}, clear=True)
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(self):
        """Test that SaslConfig.FromEnv uses default values when no environment variables are set."""
        # Act
        config = SaslConfig.FromEnv()

        # Assert
        assert config.mechanism == SaslMechanism.PLAIN
        assert config.username == ""
        assert config.password == ""

    @patch.dict(os.environ, {"KAFKA_SASL_MECHANISM": "PLAIN"})
    def test_FromEnvWithOnlyMechanism_ShouldUseDefaultCredentials(self):
        """Test that SaslConfig.FromEnv uses empty defaults when only mechanism is set."""
        # Act
        config = SaslConfig.FromEnv()

        # Assert
        assert config.mechanism == SaslMechanism.PLAIN
        assert config.username == ""
        assert config.password == ""


class TestSslConfigEdgeCases:
    """Test edge cases for SslConfig model."""

    def test_InitializeWithNonePassword_ShouldSetNone(self):
        """Test that SslConfig accepts None for optional password field."""
        # Act
        config = SslConfig(cafile="/path/ca.pem", password=None)

        # Assert
        assert config.cafile == "/path/ca.pem"
        assert config.password is None

    @patch.dict(os.environ, {}, clear=True)
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(self):
        """Test that SslConfig.FromEnv uses default values when no environment variables are set."""
        # Act
        config = SslConfig.FromEnv()

        # Assert
        assert config.cafile == ""
        assert config.certfile == ""
        assert config.keyfile == ""
        assert config.password == ""

    @patch.dict(os.environ, {"KAFKA_SSL_CAFILE": "/ca.pem"})
    def test_FromEnvWithOnlyCaFile_ShouldUseDefaultsForOthers(self):
        """Test that SslConfig.FromEnv uses defaults when only cafile is set."""
        # Act
        config = SslConfig.FromEnv()

        # Assert
        assert config.cafile == "/ca.pem"
        assert config.certfile == ""
        assert config.keyfile == ""
        assert config.password == ""


class TestKafkaConfigEdgeCases:
    """Test edge cases for KafkaConfig model."""

    @patch.dict(os.environ, {"KAFKA_ENABLE_IDEMPOTENCE": "true"})
    def test_FromEnvWithTrueIdempotence_ShouldSetTrue(self):
        """Test that KafkaConfig.FromEnv handles 'true' string for idempotence boolean."""
        # Act
        config = KafkaConfig.FromEnv()

        # Assert
        assert config.enableIdempotence == True

    @patch.dict(os.environ, {"KAFKA_ENABLE_IDEMPOTENCE": "1"})
    def test_FromEnvWithOneIdempotence_ShouldSetTrue(self):
        """Test that KafkaConfig.FromEnv handles '1' string for idempotence boolean."""
        # Act
        config = KafkaConfig.FromEnv()

        # Assert
        assert config.enableIdempotence == True

    @patch.dict(os.environ, {"KAFKA_ENABLE_IDEMPOTENCE": "yes"})
    def test_FromEnvWithYesIdempotence_ShouldSetTrue(self):
        """Test that KafkaConfig.FromEnv handles 'yes' string for idempotence boolean."""
        # Act
        config = KafkaConfig.FromEnv()

        # Assert
        assert config.enableIdempotence == True

    @patch.dict(os.environ, {}, clear=True)
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(self):
        """Test that KafkaConfig.FromEnv uses all default values when no environment variables are set."""
        # Act
        config = KafkaConfig.FromEnv()

        # Assert
        assert config.bootstrapServers == "localhost:9092"
        assert config.topicPrefix == "miraveja"
        assert config.securityProtocol == SecurityProtocol.PLAINTEXT
        assert config.enableIdempotence == True
        assert config.compressionType == CompressionType.GZIP
        assert config.sasl is None
        assert config.ssl is None

    def test_GetTopicNameWithEmptyEventType_ShouldFormatWithEmptyString(self):
        """Test that GetTopicName handles empty event type."""
        # Arrange
        config = KafkaConfig(topicPrefix="test")

        # Act
        result = config.GetTopicName("")

        # Assert
        assert result == "test..v1"

    def test_GetTopicNameWithSpecialCharacters_ShouldConvertToLowercase(self):
        """Test that GetTopicName handles special characters."""
        # Arrange
        config = KafkaConfig(topicPrefix="events")

        # Act & Assert
        assert config.GetTopicName("user@created") == "events.user@created.v1"
        assert config.GetTopicName("order#placed") == "events.order#placed.v1"

    def test_GetEventTypeFromTopicWithEmptyPrefix_ShouldExtractCorrectly(self):
        """Test that GetEventTypeFromTopic works with empty prefix."""
        # Arrange
        config = KafkaConfig(topicPrefix="")

        # Act & Assert
        assert config.GetEventTypeFromTopic(".user.created.v1") == "usercreated"

    def test_InitializeWithMultipleBootstrapServers_ShouldStoreCommaSeparated(self):
        """Test that KafkaConfig accepts comma-separated bootstrap servers."""
        # Act
        config = KafkaConfig(bootstrapServers="kafka1:9092,kafka2:9092,kafka3:9092")

        # Assert
        assert config.bootstrapServers == "kafka1:9092,kafka2:9092,kafka3:9092"

    def test_InitializeWithDefaultEventSchemasPath_ShouldSetCorrectDefault(self):
        """Test that KafkaConfig initializes with default event schemas path."""
        # Act
        config = KafkaConfig()

        # Assert
        assert config.eventSchemasPath == "/schemas/"

    def test_InitializeWithCustomEventSchemasPath_ShouldSetValue(self):
        """Test that KafkaConfig accepts custom event schemas path."""
        # Act
        config = KafkaConfig(eventSchemasPath="/custom/schemas/")

        # Assert
        assert config.eventSchemasPath == "/custom/schemas/"
