import os
import json
from typing import Optional
from pydantic import BaseModel, Field

from Miraveja.Shared.Events.Domain.Constants import (
    MILLIS_10_SEC,
    MILLIS_1_SEC,
    MILLIS_3_SEC,
    MILLIS_5_SEC,
    SIZE_16_MB,
    SIZE_32_MB,
)
from Miraveja.Shared.Events.Domain.Enums import (
    CompressionType,
    ConsumerAutoOffsetReset,
    ProducerAcksLevel,
    SaslMechanism,
    SecurityProtocol,
)


class ProducerConfig(BaseModel):
    """Configuration for Kafka producer."""

    acks: ProducerAcksLevel = Field(
        default=ProducerAcksLevel.ALL, description="Acknowledgment level for Kafka producers."
    )
    retries: int = Field(default=3, description="Number of retries for failed message sends.")
    retryBackoffMillis: int = Field(
        default=MILLIS_1_SEC, description="Backoff time in milliseconds between producer retries."
    )
    maxInFlightRequests: int = Field(default=1, description="Maximum in-flight requests per connection for ordering.")
    timeoutMillis: int = Field(default=MILLIS_10_SEC, description="Timeout in milliseconds for producer requests.")

    @classmethod
    def FromEnv(cls) -> "ProducerConfig":
        """Create ProducerConfig from environment variables."""
        configData = {}

        # Only add values if they exist in environment
        if (acks := os.getenv("KAFKA_PRODUCER_ACKS")) is not None:
            configData["acks"] = acks
        if (retries := os.getenv("KAFKA_PRODUCER_RETRIES")) is not None:
            configData["retries"] = int(retries)
        if (retryBackoff := os.getenv("KAFKA_PRODUCER_RETRY_BACKOFF_MILLIS")) is not None:
            configData["retryBackoffMillis"] = int(retryBackoff)
        if (maxInFlight := os.getenv("KAFKA_PRODUCER_MAX_IN_FLIGHT_REQUESTS")) is not None:
            configData["maxInFlightRequests"] = int(maxInFlight)
        if (timeout := os.getenv("KAFKA_PRODUCER_TIMEOUT_MILLIS")) is not None:
            configData["timeoutMillis"] = int(timeout)

        return cls.model_validate(configData)


class ConsumerConfig(BaseModel):
    """Configuration for Kafka consumer."""

    groupId: str = Field(default="miraveja-group", description="Consumer group ID for Kafka consumers.")
    autoOffsetReset: ConsumerAutoOffsetReset = Field(
        default=ConsumerAutoOffsetReset.EARLIEST,
        description="Offset reset policy for consumers (e.g., 'earliest', 'latest', 'none').",
    )
    enableAutoCommit: bool = Field(default=True, description="Whether to enable auto-commit of offsets for consumers.")
    autoCommitIntervalMillis: int = Field(
        default=MILLIS_5_SEC, description="Interval in milliseconds for auto-committing offsets."
    )
    sessionTimeoutMillis: int = Field(
        default=MILLIS_10_SEC, description="Session timeout in milliseconds for consumer group management."
    )
    heartbeatIntervalMillis: int = Field(
        default=MILLIS_3_SEC, description="Heartbeat interval in milliseconds to maintain consumer group membership."
    )

    @classmethod
    def FromEnv(cls) -> "ConsumerConfig":
        """Create ConsumerConfig from environment variables."""
        configData = {}

        # Only add values if they exist in environment
        if (groupId := os.getenv("KAFKA_CONSUMER_GROUP_ID")) is not None:
            configData["groupId"] = groupId
        if (autoOffsetReset := os.getenv("KAFKA_CONSUMER_AUTO_OFFSET_RESET")) is not None:
            configData["autoOffsetReset"] = autoOffsetReset
        if (enableAutoCommit := os.getenv("KAFKA_CONSUMER_ENABLE_AUTO_COMMIT")) is not None:
            configData["enableAutoCommit"] = enableAutoCommit.lower() in ("true", "1", "yes")
        if (autoCommitInterval := os.getenv("KAFKA_CONSUMER_AUTO_COMMIT_INTERVAL_MILLIS")) is not None:
            configData["autoCommitIntervalMillis"] = int(autoCommitInterval)
        if (sessionTimeout := os.getenv("KAFKA_CONSUMER_SESSION_TIMEOUT_MILLIS")) is not None:
            configData["sessionTimeoutMillis"] = int(sessionTimeout)
        if (heartbeatInterval := os.getenv("KAFKA_CONSUMER_HEARTBEAT_INTERVAL_MILLIS")) is not None:
            configData["heartbeatIntervalMillis"] = int(heartbeatInterval)

        return cls.model_validate(configData)


class SaslConfig(BaseModel):
    """Configuration for SASL authentication."""

    mechanism: SaslMechanism = Field(
        default=SaslMechanism.PLAIN, description="SASL mechanism (e.g., 'PLAIN', 'SCRAM-SHA-256', 'SCRAM-SHA-512')."
    )
    username: str = Field(default="", description="SASL username for authentication.")
    password: str = Field(default="", description="SASL password for authentication.")

    @classmethod
    def FromEnv(cls) -> "SaslConfig":
        """Create SaslConfig from environment variables."""
        configData = {}

        # Only add values if they exist in environment
        if (mechanism := os.getenv("KAFKA_SASL_MECHANISM")) is not None:
            configData["mechanism"] = mechanism
        if (username := os.getenv("KAFKA_SASL_USERNAME")) is not None:
            configData["username"] = username
        if (password := os.getenv("KAFKA_SASL_PASSWORD")) is not None:
            configData["password"] = password

        return cls.model_validate(configData)


class SslConfig(BaseModel):
    """Configuration for SSL encryption."""

    cafile: str = Field(default="", description="Path to CA certificate file for SSL.")
    certfile: str = Field(default="", description="Path to client certificate file for SSL.")
    keyfile: str = Field(default="", description="Path to client key file for SSL.")
    password: Optional[str] = Field(default="", description="Password for the client key file, if encrypted.")

    @classmethod
    def FromEnv(cls) -> "SslConfig":
        """Create SslConfig from environment variables."""
        configData = {}

        # Only add values if they exist in environment
        if (cafile := os.getenv("KAFKA_SSL_CAFILE")) is not None:
            configData["cafile"] = cafile
        if (certfile := os.getenv("KAFKA_SSL_CERTFILE")) is not None:
            configData["certfile"] = certfile
        if (keyfile := os.getenv("KAFKA_SSL_KEYFILE")) is not None:
            configData["keyfile"] = keyfile
        if (password := os.getenv("KAFKA_SSL_PASSWORD")) is not None:
            configData["password"] = password

        return cls.model_validate(configData)


class KafkaConfig(BaseModel):
    """Configuration for Kafka event system."""

    bootstrapServers: str = Field(
        default="localhost:9092", description="Comma-separated list of Kafka bootstrap servers."
    )
    topicPrefix: str = Field(default="miraveja", description="Prefix for all Kafka topics.")
    producer: ProducerConfig = Field(default_factory=ProducerConfig, description="Kafka producer configuration.")
    consumer: ConsumerConfig = Field(default_factory=ConsumerConfig, description="Kafka consumer configuration.")
    securityProtocol: SecurityProtocol = Field(
        default=SecurityProtocol.PLAINTEXT, description="Security protocol for Kafka connections."
    )
    sasl: Optional[SaslConfig] = Field(default=None, description="SASL authentication configuration.")
    ssl: Optional[SslConfig] = Field(default=None, description="SSL encryption configuration.")
    enableIdempotence: bool = Field(
        default=True, description="Enable idempotent producer for exactly-once delivery semantics."
    )
    compressionType: CompressionType = Field(
        default=CompressionType.GZIP, description="Compression type for Kafka messages."
    )
    batchSize: int = Field(default=SIZE_16_MB, description="Batch size in bytes for producer messages.")
    lingerMillis: int = Field(default=5, description="Linger time in milliseconds for batching producer messages.")
    bufferMemory: int = Field(default=SIZE_32_MB, description="Total memory size in bytes for producer buffering.")

    @classmethod
    def FromEnv(cls) -> "KafkaConfig":
        """Create KafkaConfig from environment variables."""
        configData = {}

        # Only add values if they exist in environment
        if (bootstrapServers := os.getenv("KAFKA_BOOTSTRAP_SERVERS")) is not None:
            configData["bootstrapServers"] = bootstrapServers
        if (topicPrefix := os.getenv("KAFKA_TOPIC_PREFIX")) is not None:
            configData["topicPrefix"] = topicPrefix
        if (securityProtocol := os.getenv("KAFKA_SECURITY_PROTOCOL")) is not None:
            configData["securityProtocol"] = securityProtocol
        if (enableIdempotence := os.getenv("KAFKA_ENABLE_IDEMPOTENCE")) is not None:
            configData["enableIdempotence"] = enableIdempotence.lower() in ("true", "1", "yes")
        if (compressionType := os.getenv("KAFKA_COMPRESSION_TYPE")) is not None:
            configData["compressionType"] = compressionType
        if (batchSize := os.getenv("KAFKA_BATCH_SIZE")) is not None:
            configData["batchSize"] = int(batchSize)
        if (lingerMillis := os.getenv("KAFKA_LINGER_MILLIS")) is not None:
            configData["lingerMillis"] = int(lingerMillis)
        if (bufferMemory := os.getenv("KAFKA_BUFFER_MEMORY")) is not None:
            configData["bufferMemory"] = int(bufferMemory)

        # Always add producer and consumer configs (they handle their own defaults)
        configData["producer"] = ProducerConfig.FromEnv()
        configData["consumer"] = ConsumerConfig.FromEnv()

        # Conditionally add SASL and SSL configs only if relevant env vars exist
        if os.getenv("KAFKA_SASL_MECHANISM"):
            configData["sasl"] = SaslConfig.FromEnv()
        if os.getenv("KAFKA_SSL_CAFILE"):
            configData["ssl"] = SslConfig.FromEnv()

        return cls.model_validate(configData)

    @classmethod
    def FromJsonFile(cls, filePath: str) -> "KafkaConfig":
        """Create KafkaConfig from a JSON configuration file."""
        with open(filePath, "r", encoding="utf-8") as file:
            configData = json.load(file)
        return cls.model_validate(configData)

    def GetTopicName(self, eventType: str) -> str:
        """Get the full topic name for a given event type."""
        return f"{self.topicPrefix}.{eventType.lower().replace('_', '.')}"
