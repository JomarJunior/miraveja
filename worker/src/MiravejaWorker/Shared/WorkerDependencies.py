import botocore.client
from boto3 import Session as Boto3Session
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine as DatabaseEngine
from sqlalchemy.orm import Session as DatabaseSession, sessionmaker

from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Infrastructure.Factories import SqlDatabaseManagerFactory
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig

# from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig

from MiravejaWorker.Shared.Events.Infrastructure.Kafka.EventConsumer import KafkaEventConsumer


class WorkerDependencies:
    """Registers core infrastructure dependencies for the worker service."""

    @staticmethod
    def RegisterDependencies(container: Container):
        """
        Register worker-specific infrastructure dependencies.

        This includes:
        - Logger
        - Kafka Event Consumer
        - Database engine and session management
        - Boto3 S3 client for MinIO
        - Database manager factory for UoW pattern

        Note: Configuration objects (databaseConfig, minioConfig, etc.)
        are already in the container, populated by Container.FromConfig()
        """
        # Get config objects from container (they're stored as dicts by FromConfig)

        # Register singletons (long-lived services)
        container.RegisterSingletons(
            {
                # Kafka Event Consumer - reconstruct KafkaConfig from dict
                KafkaEventConsumer.__name__: lambda container: KafkaEventConsumer(
                    config=KafkaConfig.model_validate(container.Get("kafkaConfig")),
                    logger=container.Get(ILogger.__name__),
                ),
                # Database Engine - single instance for connection pooling
                DatabaseEngine.__name__: lambda container: create_engine(
                    str(container.Get("databaseConfig").connectionUrl),
                    pool_size=container.Get("databaseConfig").maxConnections,
                    max_overflow=10,
                ),
                # Boto3 S3 Client for MinIO/S3 operations
                Boto3Session.client.__name__: lambda container: Boto3Session().client(
                    "s3",
                    endpoint_url=container.Get("minioConfig").endpointUrl,
                    aws_access_key_id=container.Get("minioConfig").accessKey,
                    aws_secret_access_key=container.Get("minioConfig").secretKey,
                    region_name=container.Get("minioConfig").region,
                    config=botocore.client.Config(
                        signature_version="s3v4",
                        s3={"addressing_style": "path"},
                    ),
                ),
            }
        )

        # Register factories (created per request/use)
        container.RegisterFactories(
            {
                # Database Session - new session per operation
                DatabaseSession.__name__: lambda container: sessionmaker(bind=container.Get(DatabaseEngine.__name__))(),
                # Unit of Work Factory for transactional operations
                SqlDatabaseManagerFactory.__name__: lambda container: SqlDatabaseManagerFactory(
                    resourceFactory=lambda: container.Get(DatabaseSession.__name__),
                ),
            }
        )
