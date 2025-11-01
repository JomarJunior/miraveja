import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Logging.Enums import LoggerLevel, LoggerTarget
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakConfig
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig


class LoggerConfig(BaseModel):
    name: str = Field(default="miraveja", description="Name of the logger")
    level: LoggerLevel = Field(default=LoggerLevel.INFO, description="Logging level")
    target: LoggerTarget = Field(default=LoggerTarget.CONSOLE, description="Logging target")
    format: Optional[str] = Field(default=None, description="Log message format")
    datefmt: Optional[str] = Field(default=None, description="Date format in logs")
    filename: Optional[str] = Field(default=None, description="Log file name (if target is FILE or JSON)")

    @classmethod
    def FromEnv(cls) -> "LoggerConfig":
        return cls(
            name=os.getenv("LOGGER_NAME", "miraveja"),
            level=LoggerLevel(os.getenv("LOGGER_LEVEL", "INFO")),
            target=LoggerTarget(os.getenv("LOGGER_TARGET", "CONSOLE")),
            format=os.getenv("LOGGER_FORMAT"),
            datefmt=os.getenv("LOGGER_DATEFMT"),
            filename=(
                f"{os.getenv('LOGGER_DIR', '.')}/{os.getenv('LOGGER_FILENAME')}"
                if os.getenv("LOGGER_FILENAME")
                else None
            ),
        )

    @field_validator("filename")
    @classmethod
    def ValidateFilename(cls, value: Optional[str], info: ValidationInfo) -> Optional[str]:
        if info.data.get("target") in {LoggerTarget.FILE, LoggerTarget.JSON} and not value:
            raise ValueError("Filename must be set when target is FILE or JSON")

        if value and os.path.dirname(value):
            os.makedirs(os.path.dirname(value), exist_ok=True)
        return value


class DatabaseConfig(BaseModel):
    databaseType: str = Field(default="postgresql", description="Database type (e.g., postgresql, mysql)")
    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    user: str = Field(default="user", description="Database user")
    password: str = Field(default="password", description="Database password")
    database: str = Field(default="miraveja", description="Database name")
    connectionUrl: Optional[str] = Field(..., description="Database connection URL")
    maxConnections: int = Field(default=10, description="Maximum number of database connections")

    @classmethod
    def FromEnv(cls) -> "DatabaseConfig":
        return cls(
            databaseType=os.getenv("DATABASE_TYPE", "postgresql"),
            host=os.getenv("DATABASE_HOST", "localhost"),
            port=int(os.getenv("DATABASE_PORT", "5432")),
            user=os.getenv("DATABASE_USER", "user"),
            password=os.getenv("DATABASE_PASSWORD", "password"),
            database=os.getenv("DATABASE_NAME", "miraveja"),
            connectionUrl=os.getenv("DATABASE_CONNECTION_URL", None),
            maxConnections=int(os.getenv("DATABASE_MAX_CONNECTIONS", "10")),
        )

    @field_validator("port", mode="before")
    @classmethod
    def ValidatePort(cls, value: str) -> int:
        portValue: int = int(value)

        if portValue <= 0 or portValue > 65535:
            raise ValueError("Port must be between 1 and 65535")

        return portValue

    @field_validator("connectionUrl", mode="before")
    @classmethod
    def ValidateConnectionUrl(cls, value: Optional[str], info: ValidationInfo) -> Optional[str]:
        if not value:
            value = (
                f"{info.data.get('databaseType', 'postgresql')}://"
                f"{info.data.get('user', 'user')}:"
                f"{info.data.get('password', 'password')}@"
                f"{info.data.get('host', 'localhost')}:"
                f"{info.data.get('port', 5432)}/"
                f"{info.data.get('database', 'miraveja')}"
            )
        return value

    @field_validator("maxConnections", mode="before")
    @classmethod
    def ValidateMaxConnections(cls, value: str) -> int:
        maxConnValue: int = int(value)

        if maxConnValue <= 0 or maxConnValue > 1000:
            raise ValueError("Max connections must be a positive integer and cannot exceed 1000")

        return maxConnValue


class KeycloakConfigFactory:
    @staticmethod
    def FromEnv() -> KeycloakConfig:
        return KeycloakConfig(
            serverUrl=os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080/auth/"),
            realm=os.getenv("KEYCLOAK_REALM", "miraveja"),
            clientId=os.getenv("KEYCLOAK_CLIENT_ID", "miraveja-client"),
            clientSecret=os.getenv("KEYCLOAK_CLIENT_SECRET", "secret"),
            verifyServerCertificate=os.getenv("KEYCLOAK_VERIFY_SSL", "true").lower() in ("true", "1", "yes"),
            publicKey=os.getenv("KEYCLOAK_PUBLIC_KEY"),
            tokenVerificationAlgorithm=os.getenv("KEYCLOAK_TOKEN_ALGORITHM", "RS256"),
            tokenMinimumTimeToLive=int(os.getenv("KEYCLOAK_TOKEN_MIN_TTL", "30")),
        )


class AppConfig(BaseModel):
    appName: str = Field(default="Miraveja API", description="Name of the application")
    appVersion: str = Field(default="0.0.0", description="Version of the application")
    loggerConfig: LoggerConfig = Field(default_factory=LoggerConfig.FromEnv, description="Logger configuration")
    databaseConfig: DatabaseConfig = Field(default_factory=DatabaseConfig.FromEnv, description="Database configuration")
    keycloakConfig: KeycloakConfig = Field(
        default_factory=KeycloakConfigFactory.FromEnv, description="Keycloak configuration"
    )
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
            keycloakConfig=KeycloakConfigFactory.FromEnv(),
            kafkaConfig=KafkaConfig.FromEnv(),
            minIoConfig=MinIoConfig.FromEnv(),
            debug=os.getenv("DEBUG", "false").lower() in ("true", "1", "yes"),
        )
