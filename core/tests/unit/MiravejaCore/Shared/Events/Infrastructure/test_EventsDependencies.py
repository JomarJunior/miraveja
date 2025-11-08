"""Unit tests for EventsDependencies module."""

from unittest.mock import MagicMock, patch

import pytest

from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Events.Domain.Interfaces import IEventProducer
from MiravejaCore.Shared.Events.Infrastructure.EventsDependencies import EventsDependencies
from MiravejaCore.Shared.Events.Infrastructure.Kafka.Services import KafkaEventProducer
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class TestEventsDependencies:
    """Test cases for EventsDependencies configuration."""

    def test_RegisterDependencies_ShouldRegisterEventProducer(self):
        """Test that RegisterDependencies registers IEventProducer as singleton."""
        container = Container()

        # Setup mock logger and kafka config
        mock_logger = MagicMock(spec=ILogger)
        mock_kafka_config = {"brokers": "localhost:9092", "topic": "test-topic", "security": None}
        container.instances[ILogger.__name__] = mock_logger
        container.instances["kafkaConfig"] = mock_kafka_config

        # Register dependencies
        EventsDependencies.RegisterDependencies(container)

        # Verify IEventProducer is registered
        producer = container.Get(IEventProducer.__name__)
        assert producer is not None
        assert isinstance(producer, KafkaEventProducer)

    def test_RegisterDependencies_ShouldRegisterEventDispatcher(self):
        """Test that RegisterDependencies registers EventDispatcher as factory."""
        container = Container()

        # Setup mock dependencies
        mock_logger = MagicMock(spec=ILogger)
        mock_producer = MagicMock(spec=IEventProducer)
        mock_kafka_config = {"brokers": "localhost:9092", "topic": "test-topic", "security": None}
        container.instances[ILogger.__name__] = mock_logger
        container.instances["kafkaConfig"] = mock_kafka_config
        container.instances[IEventProducer.__name__] = mock_producer

        # Register dependencies
        EventsDependencies.RegisterDependencies(container)

        # Verify EventDispatcher is registered as factory
        dispatcher = container.Get(EventDispatcher.__name__)
        assert dispatcher is not None
        assert isinstance(dispatcher, EventDispatcher)

    def test_RegisterDependencies_EventProducerFactory_ShouldUseKafkaConfig(self):
        """Test that event producer factory uses KafkaConfig from container."""
        container = Container()

        # Setup dependencies
        mock_logger = MagicMock(spec=ILogger)
        kafka_config_dict = {
            "bootstrapServers": "localhost:9092",
            "topicPrefix": "events",
        }
        container.instances[ILogger.__name__] = mock_logger
        container.instances["kafkaConfig"] = kafka_config_dict

        # Register dependencies
        EventsDependencies.RegisterDependencies(container)

        # Get producer and verify it was created (we can't access private _config easily)
        producer = container.Get(IEventProducer.__name__)
        assert producer is not None
        assert isinstance(producer, KafkaEventProducer)

    def test_RegisterDependencies_EventDispatcherFactory_ShouldInjectDependencies(self):
        """Test that event dispatcher factory injects producer and logger."""
        container = Container()

        # Setup dependencies
        mock_logger = MagicMock(spec=ILogger)
        mock_producer = MagicMock(spec=IEventProducer)
        kafka_config_dict = {
            "bootstrapServers": "localhost:9092",
            "topicPrefix": "test",
        }
        container.instances[ILogger.__name__] = mock_logger
        container.instances["kafkaConfig"] = kafka_config_dict
        container.instances[IEventProducer.__name__] = mock_producer

        # Register dependencies
        EventsDependencies.RegisterDependencies(container)

        # Get dispatcher and verify it was created with dependencies
        dispatcher = container.Get(EventDispatcher.__name__)
        assert dispatcher._eventProducer == mock_producer
        assert dispatcher._logger == mock_logger

    def test_RegisterDependencies_MultipleDispatcherInstances_ShouldCreateNewInstances(self):
        """Test that EventDispatcher factory creates new instances each time."""
        container = Container()

        # Setup dependencies
        mock_logger = MagicMock(spec=ILogger)
        mock_producer = MagicMock(spec=IEventProducer)
        mock_kafka_config = {"brokers": "localhost:9092", "topic": "test-topic", "security": None}
        container.instances[ILogger.__name__] = mock_logger
        container.instances["kafkaConfig"] = mock_kafka_config
        container.instances[IEventProducer.__name__] = mock_producer

        # Register dependencies
        EventsDependencies.RegisterDependencies(container)

        # Get multiple dispatcher instances
        dispatcher1 = container.Get(EventDispatcher.__name__)
        dispatcher2 = container.Get(EventDispatcher.__name__)

        # Verify they are different instances (factory pattern)
        assert dispatcher1 is not dispatcher2

    def test_RegisterDependencies_EventProducerSingleton_ShouldReturnSameInstance(self):
        """Test that IEventProducer singleton returns same instance."""
        container = Container()

        # Setup dependencies
        mock_logger = MagicMock(spec=ILogger)
        mock_kafka_config = {"brokers": "localhost:9092", "topic": "test-topic", "security": None}
        container.instances[ILogger.__name__] = mock_logger
        container.instances["kafkaConfig"] = mock_kafka_config

        # Register dependencies
        EventsDependencies.RegisterDependencies(container)

        # Get multiple producer instances
        producer1 = container.Get(IEventProducer.__name__)
        producer2 = container.Get(IEventProducer.__name__)

        # Verify they are the same instance (singleton pattern)
        assert producer1 is producer2

    @patch("MiravejaCore.Shared.Events.Infrastructure.EventsDependencies.KafkaEventProducer")
    def test_RegisterDependencies_EventProducerInitialization_ShouldPassCorrectParameters(
        self, mock_kafka_producer_class
    ):
        """Test that KafkaEventProducer is initialized with correct parameters."""
        container = Container()

        # Setup dependencies
        mock_logger = MagicMock(spec=ILogger)
        kafka_config_dict = {
            "bootstrapServers": "broker1:9092,broker2:9092",
            "topicPrefix": "production",
        }
        container.instances[ILogger.__name__] = mock_logger
        container.instances["kafkaConfig"] = kafka_config_dict

        # Setup mock to return a mock producer instance
        mock_producer_instance = MagicMock()
        mock_kafka_producer_class.return_value = mock_producer_instance

        # Register dependencies
        EventsDependencies.RegisterDependencies(container)

        # Get producer (triggers factory)
        producer = container.Get(IEventProducer.__name__)

        # Verify KafkaEventProducer was called with correct arguments
        mock_kafka_producer_class.assert_called_once()
        call_kwargs = mock_kafka_producer_class.call_args[1]
        assert isinstance(call_kwargs["config"], KafkaConfig)
        assert call_kwargs["config"].bootstrapServers == "broker1:9092,broker2:9092"
        assert call_kwargs["config"].topicPrefix == "production"
        assert call_kwargs["logger"] == mock_logger
