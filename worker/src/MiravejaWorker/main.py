import asyncio
from MiravejaCore.Gallery.Domain.Events import DomainEvent
from dotenv import load_dotenv

from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Infrastructure.EventsDependencies import EventsDependencies
from MiravejaCore.Shared.Logging.Factories import LoggerFactory
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Gallery.Domain.Events import ImageMetadataRegisteredEvent

from MiravejaWorker.Configuration.Models import WorkerConfig
from MiravejaWorker.Shared.Events.Infrastructure.Kafka.EventConsumer import IEventSubscriber, KafkaEventConsumer
from MiravejaWorker.Shared.WorkerDependencies import WorkerDependencies

# Load environment variables from .env file
load_dotenv()

# Load worker configuration from environment variables
workerConfig: WorkerConfig = WorkerConfig.FromEnv()

# Initialize the Container for Dependency Injection
container = Container.FromConfig(workerConfig)

# Register core dependencies
container.RegisterSingletons(
    {
        # Register Logger
        ILogger.__name__: lambda container: LoggerFactory.CreateLogger(**workerConfig.loggerConfig.model_dump()),
    }
)

# Register infrastructure dependencies
WorkerDependencies.RegisterDependencies(container)
EventsDependencies.RegisterDependencies(container)

# TODO: Register bounded context dependencies (Gallery, Member, etc.)
# GalleryWorkerDependencies.RegisterDependencies(container)
# MemberWorkerDependencies.RegisterDependencies(container)


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
    logger.Info(f"Starting {workerConfig.workerName} v{workerConfig.workerVersion}...")

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
