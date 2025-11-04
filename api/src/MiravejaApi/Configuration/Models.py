import os
from pydantic import BaseModel, Field
from MiravejaCore.Shared.Logging.Configuration import LoggerConfig
from MiravejaCore.Shared.DatabaseManager.Domain.Configuration import DatabaseConfig
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Keycloak.Domain.Configuration import KeycloakConfig
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig


class AppConfig(BaseModel):
    appName: str = Field(default="Miraveja API", description="Name of the application")
    appVersion: str = Field(default="0.0.0", description="Version of the application")
    loggerConfig: LoggerConfig = Field(default_factory=LoggerConfig.FromEnv, description="Logger configuration")
    databaseConfig: DatabaseConfig = Field(default_factory=DatabaseConfig.FromEnv, description="Database configuration")
    keycloakConfig: KeycloakConfig = Field(default_factory=KeycloakConfig.FromEnv, description="Keycloak configuration")
    kafkaConfig: KafkaConfig = Field(
        default_factory=KafkaConfig.FromEnv, description="Kafka event system configuration"
    )
    minIoConfig: MinIoConfig = Field(default_factory=MinIoConfig.FromEnv, description="MinIO configuration")
    debug: bool = Field(default=False, description="Enable debug mode")

    @classmethod
    def FromEnv(cls) -> "AppConfig":
        return cls(
            appName=os.getenv("APP_NAME", "Miraveja API"),
            appVersion=os.getenv("APP_VERSION", "0.0.0"),
            loggerConfig=LoggerConfig.FromEnv(),
            databaseConfig=DatabaseConfig.FromEnv(),
            keycloakConfig=KeycloakConfig.FromEnv(),
            kafkaConfig=KafkaConfig.FromEnv(),
            minIoConfig=MinIoConfig.FromEnv(),
            debug=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
        )
