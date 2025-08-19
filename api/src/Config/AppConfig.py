"""
App configuration settings.
"""

import os
import re
from pydantic import Field, BaseModel, field_validator
from typing import Any, Dict, Optional
from enum import Enum

class OSType(str, Enum):
    """
    Enum for operating system types.
    """
    WINDOWS = "nt"
    LINUX = "posix"
    MACOS = "darwin"
    OTHER = "other"

class AppConfig(BaseModel):
    operating_system: OSType = OSType(os.name) if os.name in OSType._value2member_map_ else OSType.OTHER
    app_name: str = Field(..., description="The name of the application")
    version: str = Field(..., description="The version of the application")
    debug: bool = Field(False, description="Enable debug mode")
    database_url: str = Field(..., description="Database connection URL")
    port: int = Field(8000, description="Port number for the application server")
    host: str = Field("localhost", description="Host name for the application server")
    filesystem_path: str = Field(..., description="Path to store application files")
    encryption_secret: bytes = Field(..., description="Secret key for encryption")
    log_target: str = Field(..., description="Target for logging (e.g., file, console)")
    final_extension: str = Field(".enc", description="Final file extension for encrypted files")
    provider_configuration: Dict[str, Any] = Field(..., description="Configuration for image providers")
    max_workers: int = Field(4, description="Maximum number of worker threads")

    @classmethod
    def from_env(cls):
        database_url: str | None = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is required")

        # Retrieve all envs that starts with PROVIDER_
        provider_envs = {key.lower(): os.getenv(key) for key in os.environ if key.startswith("PROVIDER_")}
        if not provider_envs:
            raise ValueError("Provider configuration is required")

        return cls(
            app_name=os.getenv("APP_NAME", "MiraVeja"),
            version=os.getenv("VERSION", "1.0.0"),
            debug=os.getenv("DEBUG", "false").lower() == "true",
            database_url=database_url,
            port=int(os.getenv("PORT", 8000)),
            host=os.getenv("HOST", "localhost"),
            filesystem_path=os.getenv("FILESYSTEM_PATH", "/tmp/MiraVeja"),
            encryption_secret=os.getenv("ENCRYPTION_SECRET", "my_secret_key").encode(),
            log_target=os.getenv("LOG_TARGET", "console"),
            final_extension=os.getenv("FINAL_EXTENSION", "yummy"),
            provider_configuration=provider_envs,
            max_workers=int(os.getenv("MAX_WORKERS", 4))
        )

    @field_validator('filesystem_path')
    @classmethod
    def validate_filesystem_path(cls, value: str) -> str:
        if not os.path.isabs(value):
            raise ValueError("Filesystem path must be an absolute path")
        if not os.path.exists(value):
            raise ValueError(f"Filesystem path '{value}' does not exist")
        if not os.access(value, os.W_OK):
            raise ValueError(f"Filesystem path '{value}' is not writable")

        # Validate path characters based on the operating system    
        path_regex_unix = r"^(/[\w\s-]+)+$" # Default for Unix-like systems
        path_regex_windows = r"^[a-zA-Z]:[\\/][\w\s-]+([\\/][\w\s-]+)*$" # Windows paths can include drive letters and backslashes

        if not re.match(path_regex_unix, value) and not re.match(path_regex_windows, value):
            raise ValueError("Filesystem path contains invalid characters")
        return value

    @field_validator('port')
    @classmethod
    def validate_port(cls, value: int) -> int:
        if not (0 < value < 65536):
            raise ValueError("Port must be between 1 and 65535")
        return value
    
    @field_validator('debug')
    @classmethod
    def validate_debug(cls, value: bool) -> bool:
        if not isinstance(value, bool):
            raise ValueError("Debug must be a boolean value")
        return value
    
    @field_validator('host')
    @classmethod
    def validate_host(cls, value: str) -> str:
        if not value:
            raise ValueError("Host cannot be empty")
        return value
    
    @field_validator('app_name')
    @classmethod
    def validate_app_name(cls, value: str) -> str:
        if not value:
            raise ValueError("Application name cannot be empty")
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValueError("Application name must contain only alphanumeric characters and underscores")
        return value
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, value: str) -> str:
        if not value:
            raise ValueError("Version cannot be empty")
        version_regex = r"^\d+\.\d+\.\d+$"
        if not re.match(version_regex, value):
            raise ValueError("Version must be in the format X.Y.Z")
        return value

    @field_validator('max_workers')
    @classmethod
    def validate_max_workers(cls, value: int) -> int:
        if not (1 <= value <= 32):
            raise ValueError("Max workers must be between 1 and 32")
        return value

    def to_dict(self) -> dict:
        return {
            "app_name": self.app_name,
            "version": self.version,
            "debug": self.debug,
            "database_url": self.database_url,
            "port": self.port,
            "host": self.host,
            "filesystem_path": self.filesystem_path,
            "encryption_secret": self.encryption_secret.decode(),
            "log_target": self.log_target,
            "final_extension": self.final_extension,
            "provider_configuration": self.provider_configuration,
            "max_workers": self.max_workers,
        }