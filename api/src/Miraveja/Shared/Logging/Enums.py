from enum import Enum


class LoggerLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def __str__(self) -> str:
        return self.value


class LoggerTarget(str, Enum):
    CONSOLE = "CONSOLE"
    FILE = "FILE"
    JSON = "JSON"

    def __str__(self) -> str:
        return self.value
