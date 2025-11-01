import json
from importlib import import_module
from typing import Any, Dict, List, Optional, Type, Union
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from aiokafka.consumer.consumer import AIOKafkaConsumer

from MiravejaWorker.Shared.Events.Domain.Interfaces import IEventConsumer, IEventSubscriber

EventHandlersType = Dict[str, Dict[str, List[IEventSubscriber]]]  # Topic 1-n> EventType 1-n> Subscribers


class KafkaEventConsumer(IEventConsumer):
    ANY_EVENT_WILDCARD = "*"  # pylint: disable=C0103

    def __init__(self, config: KafkaConfig, logger: ILogger):
        self._config = config
        self._logger = logger
        self._eventHandlers: EventHandlersType = {}
        self._topics = set()
        self._totalSubscribers = 0
        self._totalSubscribedEvents = 0
        self._consumer = None

    async def Start(self, topics: Optional[List[str]] = None) -> None:

        # Define deserializer for Kafka messages
        def Deserializer(m):
            decoded = m.decode("utf-8")
            try:
                loaded = json.loads(decoded)
                return loaded
            except json.JSONDecodeError as e:
                self._logger.Error(f"Error decoding JSON message: {e}")
                return {}

        # Initialize Kafka consumer with specified topics
        self._consumer = AIOKafkaConsumer(
            *(topics if topics is not None else list(self._topics)),
            bootstrap_servers=self._config.bootstrapServers,
            group_id=self._config.consumer.groupId,
            auto_offset_reset=self._config.consumer.autoOffsetReset.value,
            enable_auto_commit=self._config.consumer.enableAutoCommit,
            value_deserializer=Deserializer,
        )

        await self._consumer.start()
        self._logger.Info("KafkaEventConsumer started.")
        self._logger.Info(f"Listening for events on topics: {self._topics}.")
        self._logger.Info(f"Total subscribers: {self._totalSubscribers}")
        self._logger.Info(f"Total subscribed events: {self._totalSubscribedEvents}")
        self._logger.Info(f"Total subscribed topics: {len(self._topics)}")

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
            eventType = event.type
            topic = message.topic

            # Handle specific event type subscribers
            if eventType in self._eventHandlers.get(topic, {}):
                for handler in self._eventHandlers[topic][eventType]:
                    await handler.Handle(event)

            # Handle wildcard subscribers
            if KafkaEventConsumer.ANY_EVENT_WILDCARD in self._eventHandlers.get(topic, {}):
                for handler in self._eventHandlers[topic][KafkaEventConsumer.ANY_EVENT_WILDCARD]:
                    await handler.Handle(event)

        except Exception as e:
            self._logger.Error(f"Error processing message: {str(e)}")

    def Subscribe(
        self, event: Union[Type[DomainEvent], str], subscriber: IEventSubscriber, topic: Optional[str] = None
    ) -> None:
        # Validate event type
        if isinstance(event, str) and event != KafkaEventConsumer.ANY_EVENT_WILDCARD:
            raise ValueError("Invalid event type string provided for subscription.")
        eventType: str = event.type if not isinstance(event, str) else event

        # Determine topic if not provided
        if topic is None:
            if eventType == KafkaEventConsumer.ANY_EVENT_WILDCARD:
                raise ValueError("Topic must be provided when subscribing to wildcard events.")

            topic = self._config.GetTopicName(eventType)

        # Initialize nested dictionaries if they don't exist
        if topic not in self._eventHandlers:
            self._eventHandlers[topic] = {}
        if eventType not in self._eventHandlers[topic]:
            self._eventHandlers[topic][eventType] = []
            self._totalSubscribedEvents += 1

        # Add the subscriber to the list for the specific event type and topic
        self._eventHandlers[topic][eventType].append(subscriber)
        self._totalSubscribers += 1

        # Track all unique topics
        self._topics.add(topic)
        self._logger.Info(f"Subscriber added for event type: {eventType} on topic: {topic}")
