import json
import asyncio
from typing import Any, Dict, List, Optional
from confluent_kafka import Producer as KafkaProducer, KafkaError, Message

from Miraveja.Shared.Events.Domain.Configuration import KafkaConfig
from Miraveja.Shared.Events.Domain.Enums import SecurityProtocol
from Miraveja.Shared.Events.Domain.Interfaces import DomainEvent, IEventProducer
from Miraveja.Shared.Logging.Interfaces import ILogger


class KafkaEventProducer(IEventProducer):
    """Implementation of IEventProducer for dispatching events to Kafka."""

    def __init__(
        self,
        config: KafkaConfig,
        logger: ILogger,
    ):
        self._logger = logger
        self._config = config
        self._producer: Optional[KafkaProducer] = None
        self._InitializeKafkaProducer()

    @property
    def _producerConfig(self) -> Dict[str, Any]:
        config = {
            "bootstrap.servers": self._config.bootstrapServers,
            "acks": self._config.producer.acks,
            "retries": self._config.producer.retries,
            "retry.backoff.ms": self._config.producer.retryBackoffMillis,
            "max.in.flight.requests.per.connection": self._config.producer.maxInFlightRequests,
            "request.timeout.ms": self._config.producer.timeoutMillis,
            "enable.idempotence": self._config.enableIdempotence,
            "compression.type": self._config.compressionType,
            "batch.size": self._config.batchSize,
            "linger.ms": self._config.lingerMillis,
            "security.protocol": self._config.securityProtocol.upper(),
        }

        # Add SASL configuration if needed
        if self._config.sasl is not None:
            if self._config.securityProtocol in {SecurityProtocol.SASL_PLAINTEXT, SecurityProtocol.SASL_SSL}:
                # Only add sasl config if security protocol requires it, even if sasl config is partially provided
                config.update(
                    {
                        "sasl.mechanism": self._config.sasl.mechanism,
                        "sasl.username": self._config.sasl.username,
                        "sasl.password": self._config.sasl.password,
                    }
                )

        # Add SSL configuration if needed
        if self._config.ssl is not None:
            if self._config.securityProtocol in {SecurityProtocol.SSL, SecurityProtocol.SASL_SSL}:
                # Only add ssl config if security protocol requires it, even if ssl config is partially provided
                if self._config.ssl.cafile is not None:
                    config["ssl.ca.location"] = self._config.ssl.cafile
                if self._config.ssl.certfile is not None:
                    config["ssl.certificate.location"] = self._config.ssl.certfile
                if self._config.ssl.keyfile is not None:
                    config["ssl.key.location"] = self._config.ssl.keyfile
                if self._config.ssl.password is not None:
                    config["ssl.key.password"] = self._config.ssl.password

        return config

    def _InitializeKafkaProducer(self) -> None:
        """Initialize the Kafka producer if not already initialized."""
        if self._producer is None:
            try:
                producerConfig = self._producerConfig
                self._producer = KafkaProducer(producerConfig)
                self._logger.Info("Kafka producer initialized successfully.")

            except Exception as ex:
                self._logger.Error(f"Failed to initialize Kafka producer: {ex}")
                raise ex

    def _DeliveryCallback(self, err: KafkaError, msg: Message) -> None:
        """Callback function to handle delivery reports from Kafka."""
        if err is not None:
            if err.fatal():
                self._logger.Error(f"Fatal message delivery error: {err.str()}")
            elif err.retriable():
                self._logger.Warning(f"Retriable message delivery error: {err.str()}")
            else:
                self._logger.Error(f"Message delivery error: {err.str()}")
        else:
            self._logger.Debug(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

    async def Produce(self, event: DomainEvent) -> None:
        """Produce a single domain event to Kafka."""
        if self._producer is None:
            raise RuntimeError("Kafka producer is not initialized.")

        topicName = self._config.GetTopicName(event.type)
        message = event.ToKafkaMessage()

        try:
            self._logger.Debug(f"Producing message to topic '{topicName}': {message}")

            # Serialize message to JSON
            messageValue = json.dumps(message).encode("utf-8")

            # Use aggregate ID as partition key for ordering
            partitionKey = event.aggregateId.encode("utf-8") if event.aggregateId else None

            # Produce message asynchronously with callback
            await asyncio.to_thread(
                self._producer.produce,
                topic=topicName,
                key=partitionKey,
                value=messageValue,
                on_delivery=self._DeliveryCallback,
            )

        except Exception as ex:
            self._logger.Error(f"Failed to produce message to Kafka: {ex}")
            raise ex

    async def ProduceAll(self, events: List[DomainEvent]) -> None:
        """Produce all provided domain events to Kafka."""
        if self._producer is None:
            raise RuntimeError("Kafka producer is not initialized.")

        if len(events) == 0:
            self._logger.Info("No events to produce.")
            return

        self._logger.Info(f"Producing {len(events)} events to Kafka.")

        try:
            # await self.Produce(event)
            results = await asyncio.gather(*(self.Produce(event) for event in events), return_exceptions=True)
            # Poll for delivery reports (non-blocking)
            await asyncio.to_thread(self._producer.poll, 0)

            for result in results:
                if isinstance(result, Exception):
                    self._logger.Error(f"Kafka produce error for event batch: {result}")

            # Wait for all messages to be delivered
            remaining = await asyncio.to_thread(
                self._producer.flush, timeout=self._config.producer.timeoutMillis / 1000
            )
            if remaining > 0:
                self._logger.Warning(f"{remaining} messages were not delivered before flush timeout.")

            self._logger.Info(f"Successfully produced {len(events) - remaining} events to Kafka.")

        except Exception as ex:
            self._logger.Error(f"Failed to produce events to Kafka: {ex}")
            raise ex

    def Close(self) -> None:
        """Close the Kafka producer, ensuring all messages are flushed."""
        if self._producer is not None:
            remaining = self._producer.flush(
                timeout=self._config.producer.timeoutMillis / 1000
            )  # Wait for messages to be delivered
            if remaining > 0:
                self._logger.Warning(f"Kafka producer closed with {remaining} messages still pending delivery.")
            else:
                self._logger.Info("All messages successfully delivered before closing Kafka producer.")
            self._producer = None
            self._logger.Info("Kafka producer closed.")
