import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo


class DatabaseConfig(BaseModel):
    """Configuration for database connections across MiraVeja services."""

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
