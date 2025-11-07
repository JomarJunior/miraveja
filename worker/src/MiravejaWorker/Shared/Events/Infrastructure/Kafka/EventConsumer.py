import json
from importlib import import_module
from typing import Any, Dict, List, Optional, Type, Union
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from aiokafka.consumer.consumer import AIOKafkaConsumer

from MiravejaWorker.Shared.Events.Domain.Interfaces import IEventConsumer, IEventSubscriber

EventHandlersType = Dict[str, List[IEventSubscriber]]  # EventType 1-n> Subscribers


class KafkaEventConsumer(IEventConsumer):
    def __init__(self, config: KafkaConfig, logger: ILogger):
        self._config = config
        self._logger = logger
        self._eventHandlers: EventHandlersType = {}
        self._events: set = set()
        self._totalSubscribers = 0
        self._consumer = None

    async def Start(self, events: Optional[List[str]] = None) -> None:
        # Define deserializer for Kafka messages
        def Deserializer(m):
            decoded = m.decode("utf-8")
            try:
                loaded = json.loads(decoded)
                return loaded
            except json.JSONDecodeError as e:
                self._logger.Error(f"Error decoding JSON message: {e}")
                return {}

        # Initialize Kafka consumer with specified events
        listenEvents = events if events is not None else list(self._events)
        self._consumer = AIOKafkaConsumer(
            *listenEvents,
            bootstrap_servers=self._config.bootstrapServers,
            group_id=self._config.consumer.groupId,
            auto_offset_reset=self._config.consumer.autoOffsetReset.value,
            enable_auto_commit=self._config.consumer.enableAutoCommit,
            value_deserializer=Deserializer,
        )

        await self._consumer.start()
        self._logger.Info("KafkaEventConsumer started.")
        self._logger.Info(f"Listening for events: {listenEvents}.")
        self._logger.Info(f"Total subscribers: {self._totalSubscribers}")

        try:
            async for message in self._consumer:
                await self._ProcessMessage(message)
        finally:
            await self.Stop()

    async def Stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()
            self._logger.Info("KafkaEventConsumer stopped.")

    async def _ProcessMessage(self, message) -> None:
        try:
            eventClass: Union[Type[DomainEvent], None, Any] = message.value.get("class")
            self._logger.Info(f"Raw message: {message}")
            if not eventClass:
                self._logger.Error("Received message without 'class' field.")
                return

            # Resolve event class if the message provided a string (e.g. "package.module.ClassName")
            parsedEventClass: Optional[Type[DomainEvent]] = None
            if isinstance(eventClass, str):
                try:
                    # Try fully-qualified name first: module.Class
                    moduleName, className = eventClass.rsplit(".", 1)
                    module = import_module(moduleName)
                    parsedEventClass = getattr(module, className)
                except Exception as e:
                    self._logger.Error(f"Could not resolve event class '{eventClass}': {e}")
                    return

            if parsedEventClass is None:
                self._logger.Error(f"Event class '{eventClass}' not found.")
                return

            event = parsedEventClass.model_validate(message.value.get("payload", {}))

            # Handle specific event type subscribers
            if message.topic in self._eventHandlers:  # an event is a kafka topic
                for handler in self._eventHandlers[message.topic]:
                    await handler.Handle(event)

        except Exception as e:
            self._logger.Error(f"Error processing message: {str(e)}")

    def Subscribe(
        self,
        event: Union[Type[DomainEvent], str],
        subscriber: IEventSubscriber,
    ) -> None:
        # Validate event type
        eventType: str = event.type if not isinstance(event, str) else event
        eventVersion: int = event.version if not isinstance(event, str) else 1
        topicName: str = self._config.GetTopicName(eventType, eventVersion)

        # Initialize nested dictionaries if they don't exist
        if topicName not in self._eventHandlers:
            self._eventHandlers[topicName] = []
            self._events.add(topicName)

        # Add the subscriber to the list for the specific event type
        self._eventHandlers[topicName].append(subscriber)
        self._totalSubscribers += 1

        self._logger.Info(f"Subscriber added for event: {eventType}")
