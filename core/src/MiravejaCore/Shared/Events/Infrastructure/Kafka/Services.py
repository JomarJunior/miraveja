import json
import asyncio
from typing import Any, Dict, List, Optional
from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Events.Domain.Enums import SecurityProtocol
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent, IEventProducer
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class KafkaEventProducer(IEventProducer):
    """Implementation of IEventProducer for dispatching events to Kafka using AIOKafka."""

    def __init__(
        self,
        config: KafkaConfig,
        logger: ILogger,
    ):
        self._logger = logger
        self._config = config
        self._producer: Optional[AIOKafkaProducer] = None

    @property
    def _producerConfig(self) -> Dict[str, Any]:
        config = {
            "bootstrap_servers": self._config.bootstrapServers,
            "acks": self._config.producer.acks,
            # "retries": self._config.producer.retries,
            "retry_backoff_ms": self._config.producer.retryBackoffMillis,
            "max_batch_size": self._config.batchSize,
            "linger_ms": self._config.lingerMillis,
            "security_protocol": self._config.securityProtocol.upper(),
            "enable_idempotence": self._config.enableIdempotence,
            "compression_type": self._config.compressionType.lower(),
            "request_timeout_ms": self._config.producer.timeoutMillis,
            # "max_in_flight_requests_per_connection": self._config.producer.maxInFlightRequests,
        }

        # Add SASL configuration if needed
        if self._config.sasl is not None:
            if self._config.securityProtocol in {SecurityProtocol.SASL_PLAINTEXT, SecurityProtocol.SASL_SSL}:
                # Only add sasl config if security protocol requires it
                config.update(
                    {
                        "sasl_mechanism": self._config.sasl.mechanism,
                        "sasl_plain_username": self._config.sasl.username,
                        "sasl_plain_password": self._config.sasl.password,
                    }
                )

        # Add SSL configuration if needed
        if self._config.ssl is not None:
            if self._config.securityProtocol in {SecurityProtocol.SSL, SecurityProtocol.SASL_SSL}:
                # Only add ssl config if security protocol requires it
                if self._config.ssl.cafile is not None:
                    config["ssl_cafile"] = self._config.ssl.cafile
                if self._config.ssl.certfile is not None:
                    config["ssl_certfile"] = self._config.ssl.certfile
                if self._config.ssl.keyfile is not None:
                    config["ssl_keyfile"] = self._config.ssl.keyfile
                if self._config.ssl.password is not None:
                    config["ssl_password"] = self._config.ssl.password

        return config

    async def _InitializeKafkaProducer(self) -> None:
        """Initialize the Kafka producer if not already initialized."""
        if self._producer is None:
            try:
                producerConfig = self._producerConfig
                self._producer = AIOKafkaProducer(**producerConfig)
                await self._producer.start()
                self._logger.Info("Kafka producer initialized successfully.")

            except Exception as ex:
                self._logger.Error(f"Failed to initialize Kafka producer: {ex}")
                raise ex

    async def _HandleDeliveryReport(self, topic: str, partition: int, offset: int) -> None:
        """Handle delivery reports from Kafka."""
        self._logger.Debug(f"Message delivered to {topic} [{partition}] at offset {offset}")

    async def Produce(self, event: DomainEvent) -> None:
        """Produce a single domain event to Kafka."""
        await self._InitializeKafkaProducer()

        if self._producer is None:
            raise RuntimeError("Kafka producer is not initialized.")

        topicName = self._config.GetTopicName(event.type, event.version)
        message = event.ToKafkaMessage()

        try:
            self._logger.Debug(f"Producing message to topic '{topicName}': {message}")

            # Serialize message to JSON
            messageValue = json.dumps(message).encode("utf-8")

            # Use aggregate ID as partition key for ordering
            partitionKey = event.aggregateId.encode("utf-8") if event.aggregateId else None

            # Produce message asynchronously
            metadata = await self._producer.send_and_wait(topic=topicName, key=partitionKey, value=messageValue)
            await self._HandleDeliveryReport(metadata.topic, metadata.partition, metadata.offset)

        except KafkaError as ex:
            self._logger.Error(f"Failed to produce message to Kafka: {ex}")
            raise ex

    async def ProduceAll(self, events: List[DomainEvent]) -> None:
        """Produce all provided domain events to Kafka."""
        await self._InitializeKafkaProducer()

        if self._producer is None:
            raise RuntimeError("Kafka producer is not initialized.")

        if len(events) == 0:
            self._logger.Info("No events to produce.")
            return

        self._logger.Info(f"Producing {len(events)} events to Kafka.")

        try:
            # Send all events in parallel
            results = await asyncio.gather(*(self.Produce(event) for event in events), return_exceptions=True)

            # Check for any errors
            for result in results:
                if isinstance(result, Exception):
                    self._logger.Error(f"Kafka produce error for event batch: {result}")

            # Flush any remaining messages
            await self._producer.flush()
            self._logger.Info(f"Successfully produced {len(events)} events to Kafka.")

        except Exception as ex:
            self._logger.Error(f"Failed to produce events to Kafka: {ex}")
            raise ex

    async def Close(self) -> None:
        """Close the Kafka producer, ensuring all messages are flushed."""
        if self._producer is not None:
            try:
                await self._producer.flush()
                self._logger.Info("All messages successfully delivered before closing Kafka producer.")
                await self._producer.stop()
                self._producer = None
                self._logger.Info("Kafka producer closed.")
            except Exception as ex:
                self._logger.Error(f"Error closing Kafka producer: {ex}")
                raise ex
