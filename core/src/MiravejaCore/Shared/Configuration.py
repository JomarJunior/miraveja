import os

from pydantic import BaseModel, Field

from MiravejaCore.Gallery.Domain.Configuration import GalleryConfig
from MiravejaCore.Shared.DatabaseManager.Domain.Configuration import DatabaseConfig
from MiravejaCore.Shared.Embeddings.Domain.Configuration import EmbeddingConfig
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Keycloak.Domain.Configuration import KeycloakConfig
from MiravejaCore.Shared.Logging.Configuration import LoggerConfig
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Shared.VectorDatabase.Domain.Configuration import QdrantConfig


class AppConfig(BaseModel):
    """Main configuration for the Miraveja applications."""

    appName: str = Field(default="Miraveja Application", description="Name of the application")
    appVersion: str = Field(default="0.0.0", description="Version of the application")
    loggerConfig: LoggerConfig = Field(default_factory=LoggerConfig.FromEnv, description="Logger configuration")
    databaseConfig: DatabaseConfig = Field(default_factory=DatabaseConfig.FromEnv, description="Database configuration")
    keycloakConfig: KeycloakConfig = Field(default_factory=KeycloakConfig.FromEnv, description="Keycloak configuration")
    kafkaConfig: KafkaConfig = Field(
        default_factory=KafkaConfig.FromEnv, description="Kafka event system configuration"
    )
    minioConfig: MinIoConfig = Field(
        default_factory=MinIoConfig.FromEnv, description="MinIO object storage configuration"
    )
    qdrantConfig: QdrantConfig = Field(
        default_factory=QdrantConfig.FromEnv, description="Qdrant vector database configuration"
    )
    embeddingConfig: EmbeddingConfig = Field(
        default_factory=EmbeddingConfig.FromEnv, description="Embedding configuration"
    )
    galleryConfig: GalleryConfig = Field(
        default_factory=GalleryConfig.FromEnv, description="Gallery module specific configuration"
    )

    @classmethod
    def FromEnv(cls) -> "AppConfig":
        return cls(
            appName=os.getenv("APP_NAME", "Miraveja Application"),
            appVersion=os.getenv("APP_VERSION", "0.0.0"),
            loggerConfig=LoggerConfig.FromEnv(),
            databaseConfig=DatabaseConfig.FromEnv(),
            keycloakConfig=KeycloakConfig.FromEnv(),
            kafkaConfig=KafkaConfig.FromEnv(),
            minioConfig=MinIoConfig.FromEnv(),
            qdrantConfig=QdrantConfig.FromEnv(),
            embeddingConfig=EmbeddingConfig.FromEnv(),
            galleryConfig=GalleryConfig.FromEnv(),
        )
