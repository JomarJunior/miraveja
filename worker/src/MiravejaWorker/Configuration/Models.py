import os
from pydantic import BaseModel, Field
from MiravejaCore.Shared.Logging.Configuration import LoggerConfig
from MiravejaCore.Shared.Logging.Enums import LoggerTarget
from MiravejaCore.Shared.DatabaseManager.Domain.Configuration import DatabaseConfig
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Shared.VectorDatabase.Domain.Configuration import QdrantConfig


class WorkerConfig(BaseModel):
    """Main configuration for the worker service."""

    workerName: str = Field(default="MiravejaWorker", description="Name of the worker service")
    workerVersion: str = Field(default="0.0.0", description="Version of the worker service")
    loggerConfig: LoggerConfig = Field(
        default_factory=lambda: LoggerConfig.FromEnv(defaultName="MiravejaWorker", defaultTarget=LoggerTarget.FILE),
        description="Logger configuration",
    )
    databaseConfig: DatabaseConfig = Field(default_factory=DatabaseConfig.FromEnv, description="Database configuration")
    kafkaConfig: KafkaConfig = Field(
        default_factory=KafkaConfig.FromEnv, description="Kafka event system configuration"
    )
    minIoConfig: MinIoConfig = Field(default_factory=MinIoConfig.FromEnv, description="MinIO configuration")
    qdrantConfig: QdrantConfig = Field(default_factory=QdrantConfig.FromEnv, description="Qdrant configuration")
    debug: bool = Field(default=False, description="Enable debug mode")

    @classmethod
    def FromEnv(cls) -> "WorkerConfig":
        return cls(
            workerName=os.getenv("WORKER_NAME", "MiravejaWorker"),
            workerVersion=os.getenv("WORKER_VERSION", "0.0.0"),
            loggerConfig=LoggerConfig.FromEnv(defaultName="MiravejaWorker", defaultTarget=LoggerTarget.FILE),
            databaseConfig=DatabaseConfig.FromEnv(),
            kafkaConfig=KafkaConfig.FromEnv(),
            minIoConfig=MinIoConfig.FromEnv(),
            qdrantConfig=QdrantConfig.FromEnv(),
            debug=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
        )
