import botocore.client
import httpx
from boto3 import Session as Boto3Session
from MiravejaCore.Shared.Configuration import DatabaseConfig
from MiravejaCore.Shared.DatabaseManager.Infrastructure.Factories import SqlDatabaseManagerFactory
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Events.Domain.Interfaces import IEventConsumer
from MiravejaCore.Shared.Events.Domain.Services import (
    EventDeserializerService,
    EventFactory,
    EventRegistry,
    EventValidatorService,
    eventRegistry,
)
from MiravejaCore.Shared.Events.Infrastructure.Json.Registry import JsonSchemaRegistry
from MiravejaCore.Shared.Events.Infrastructure.Kafka.Services import KafkaEventConsumer
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine as DatabaseEngine
from sqlalchemy.orm import Session as DatabaseSession
from sqlalchemy.orm import sessionmaker

# from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig


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
        container.RegisterFactories(
            {
                # Registries
                EventRegistry.__name__: lambda container: eventRegistry,
                JsonSchemaRegistry.__name__: lambda container: JsonSchemaRegistry(
                    config=KafkaConfig.model_validate(container.Get("kafkaConfig"))
                ),
                # Services
                IEventConsumer.__name__: lambda container: KafkaEventConsumer(
                    config=KafkaConfig.model_validate(container.Get("kafkaConfig")),
                    eventFactory=container.Get(EventFactory.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                EventDeserializerService.__name__: lambda container: EventDeserializerService(
                    _eventRegistry=container.Get(EventRegistry.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                EventValidatorService.__name__: lambda container: EventValidatorService(
                    schemaRegistry=container.Get(JsonSchemaRegistry.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                EventFactory.__name__: lambda container: EventFactory(
                    deserializerService=container.Get(EventDeserializerService.__name__),
                    validatorService=container.Get(EventValidatorService.__name__),
                ),
            }
        )

        databaseConfig: DatabaseConfig = DatabaseConfig.model_validate(container.Get("databaseConfig"))
        minioConfig: MinIoConfig = MinIoConfig.model_validate(container.Get("minioConfig"))
        # Register singletons (long-lived services)
        container.RegisterSingletons(
            {
                # Kafka Event Consumer - reconstruct KafkaConfig from dict
                KafkaEventConsumer.__name__: lambda container: KafkaEventConsumer(
                    config=KafkaConfig.model_validate(container.Get("kafkaConfig")),
                    logger=container.Get(ILogger.__name__),
                    eventFactory=container.Get(EventFactory.__name__),
                ),
                # Database Engine - single instance for connection pooling
                DatabaseEngine.__name__: lambda container: create_engine(
                    str(databaseConfig.connectionUrl),
                    pool_size=databaseConfig.maxConnections,
                    max_overflow=databaseConfig.maxConnections // 2,
                ),
                # Boto3 S3 Client for MinIO/S3 operations
                Boto3Session.client.__name__: lambda container: Boto3Session().client(
                    "s3",
                    endpoint_url=minioConfig.endpointUrl,
                    aws_access_key_id=minioConfig.accessKey,
                    aws_secret_access_key=minioConfig.secretKey,
                    region_name=minioConfig.region,
                    config=botocore.client.Config(
                        signature_version="s3v4",
                        s3={"addressing_style": "path"},
                    ),
                ),
                # Httpx Async Client for HTTP operations
                httpx.AsyncClient.__name__: lambda container: httpx.AsyncClient(
                    verify=False,
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
