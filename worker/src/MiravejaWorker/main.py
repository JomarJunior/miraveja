import asyncio
from dotenv import load_dotenv

from MiravejaCore.Shared.Configuration import AppConfig
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Gallery.Domain.Events import DomainEvent
from MiravejaCore.Shared.Events.Infrastructure.EventsDependencies import EventsDependencies
from MiravejaCore.Shared.Logging.Factories import LoggerFactory
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Gallery.Domain.Events import ImageMetadataRegisteredEvent

from MiravejaWorker.Shared.Events.Infrastructure.Kafka.EventConsumer import IEventSubscriber, KafkaEventConsumer
from MiravejaWorker.Shared.WorkerDependencies import WorkerDependencies

# Load environment variables from .env file
load_dotenv()

# Load worker configuration from environment variables
appConfig: AppConfig = AppConfig.FromEnv()

# Initialize the Container for Dependency Injection
container = Container.FromConfig(appConfig)

# Register core dependencies
container.RegisterSingletons(
    {
        # Register Logger
        ILogger.__name__: lambda container: LoggerFactory.CreateLogger(**appConfig.loggerConfig.model_dump()),
    }
)

# Register infrastructure dependencies
WorkerDependencies.RegisterDependencies(container)
EventsDependencies.RegisterDependencies(container)


class TestSubscriber(IEventSubscriber):
    async def Handle(self, event: DomainEvent) -> None:
        logger = container.Get(ILogger.__name__)
        logger.Info(f"Processing {event.type}")
        # Simulate processing logic
        await asyncio.sleep(1)
        logger.Info(f"Successfully processed {event.type}")


async def Main():
    """Main entry point for the MiravejaWorker service."""
    logger = container.Get(ILogger.__name__)
    logger.Info(f"Starting {appConfig.appName} v{appConfig.appVersion}...")

    kafkaConsumer: KafkaEventConsumer = container.Get(KafkaEventConsumer.__name__)

    kafkaConsumer.Subscribe(ImageMetadataRegisteredEvent, TestSubscriber())

    try:
        # Start consuming events from Kafka
        await kafkaConsumer.Start()
    except KeyboardInterrupt:
        logger.Info("Worker stopping due to keyboard interrupt.")
        await kafkaConsumer.Stop()
    except Exception as e:
        logger.Critical(f"Worker encountered a critical error: {str(e)}")
        await kafkaConsumer.Stop()
        raise


if __name__ == "__main__":
    asyncio.run(Main())
