import os
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from MiravejaCore.Shared.Logging.Enums import LoggerLevel, LoggerTarget


class LoggerConfig(BaseModel):
    """Configuration for logging across MiraVeja services."""

    name: str = Field(default="miraveja", description="Name of the logger")
    level: LoggerLevel = Field(default=LoggerLevel.INFO, description="Logging level")
    target: LoggerTarget = Field(default=LoggerTarget.CONSOLE, description="Logging target")
    format: Optional[str] = Field(default=None, description="Log message format")
    datefmt: Optional[str] = Field(default=None, description="Date format in logs")
    filename: Optional[str] = Field(default=None, description="Log file name (if target is FILE or JSON)")

    @classmethod
    def FromEnv(
        cls, defaultName: str = "miraveja", defaultTarget: LoggerTarget = LoggerTarget.CONSOLE
    ) -> "LoggerConfig":
        """
        Create LoggerConfig from environment variables.

        Args:
            defaultName: Default logger name if LOGGER_NAME is not set
            defaultTarget: Default logging target if LOGGER_TARGET is not set
        """
        target = LoggerTarget(os.getenv("LOGGER_TARGET", defaultTarget.value))

        # Determine filename based on target and environment variables
        filename = None
        if os.getenv("LOGGER_FILENAME"):
            filename = f"{os.getenv('LOGGER_DIR', '.')}/{os.getenv('LOGGER_FILENAME')}"
        elif target in {LoggerTarget.FILE, LoggerTarget.JSON}:
            # Provide default filename if target requires it but none is set
            loggerDir = os.getenv("LOGGER_DIR", "./logs")
            filename = f"{loggerDir}/{defaultName.lower()}.log"

        return cls(
            name=os.getenv("LOGGER_NAME", defaultName),
            level=LoggerLevel(os.getenv("LOGGER_LEVEL", "INFO")),
            target=target,
            format=os.getenv("LOGGER_FORMAT"),
            datefmt=os.getenv("LOGGER_DATEFMT"),
            filename=filename,
        )

    @field_validator("filename")
    @classmethod
    def ValidateFilename(cls, value: Optional[str], info: ValidationInfo) -> Optional[str]:
        if info.data.get("target") in {LoggerTarget.FILE, LoggerTarget.JSON} and not value:
            raise ValueError("Filename must be set when target is FILE or JSON")

        if value and os.path.dirname(value):
            os.makedirs(os.path.dirname(value), exist_ok=True)
        return value
