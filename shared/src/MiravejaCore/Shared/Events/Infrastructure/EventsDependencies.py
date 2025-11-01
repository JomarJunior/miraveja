from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Events.Domain.Interfaces import IEventProducer
from MiravejaCore.Shared.Events.Infrastructure.Kafka.Services import KafkaEventProducer
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class EventsDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        container.RegisterSingletons(
            {
                # Producers
                IEventProducer.__name__: lambda container: KafkaEventProducer(
                    config=KafkaConfig.model_validate(container.Get("kafkaConfig")),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )

        container.RegisterFactories(
            {
                # Dispatcher
                EventDispatcher.__name__: lambda container: EventDispatcher(
                    eventProducer=container.Get(IEventProducer.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
