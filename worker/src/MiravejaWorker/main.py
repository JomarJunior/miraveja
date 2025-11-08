import asyncio
from dotenv import load_dotenv

from MiravejaCore.Shared.Configuration import AppConfig
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Gallery.Domain.Events import DomainEvent
from MiravejaCore.Shared.Events.Infrastructure.EventsDependencies import EventsDependencies
from MiravejaCore.Shared.Logging.Factories import LoggerFactory
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Events.Infrastructure.Kafka.Services import IEventSubscriber, KafkaEventConsumer

from MiravejaWorker.Shared.WorkerDependencies import WorkerDependencies
from MiravejaWorker.Member.Infrastructure.MemberSubscribers import MemberSubscribers
from MiravejaWorker.Member.Infrastructure.MemberDependencies import MemberDependencies

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
MemberDependencies.RegisterDependencies(container)

# Register Subscribers
eventConsumer: KafkaEventConsumer = container.Get(KafkaEventConsumer.__name__)
MemberSubscribers.RegisterSubscribers(eventConsumer, container)


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

    try:
        # Start consuming events from Kafka
        await eventConsumer.Start()
    except KeyboardInterrupt:
        logger.Info("Worker stopping due to keyboard interrupt.")
        await eventConsumer.Stop()
    except Exception as e:
        logger.Critical(f"Worker encountered a critical error: {str(e)}")
        await eventConsumer.Stop()
        raise


if __name__ == "__main__":
    asyncio.run(Main())
