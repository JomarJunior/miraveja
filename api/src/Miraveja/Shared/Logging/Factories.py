import logging
from typing import Dict, Any, Optional, Tuple
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.Logging.Models import Logger
from Miraveja.Shared.Logging.Enums import LoggerLevel, LoggerTarget
from Miraveja.Shared.Logging.Exceptions import LoggerAlreadyExistsException


TARGET_HANDLER_MAP: Dict[LoggerTarget, type[logging.Handler]] = {
    LoggerTarget.CONSOLE: logging.StreamHandler,
    LoggerTarget.FILE: logging.FileHandler,
    LoggerTarget.JSON: logging.FileHandler,  # Placeholder; would need a custom JSON handler
}

DEFAULT_HANDLER: type[logging.Handler] = logging.StreamHandler
DEFAULT_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATEFMT: str = "%Y-%m-%d %H:%M:%S"


class LoggerFactory:
    @staticmethod
    def CreateLogger(
        *args: Tuple[Any, ...],
        name: str = "miraveja",
        level: LoggerLevel = LoggerLevel.INFO,
        target: LoggerTarget = LoggerTarget.CONSOLE,
        format: Optional[str] = None,
        datefmt: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> ILogger:
        logger = logging.getLogger(name)
        if logger.hasHandlers():
            raise LoggerAlreadyExistsException(name)

        LoggerFactory._ConfigureLogging(
            *args, logger=logger, level=level, target=target, format=format, datefmt=datefmt, **kwargs
        )
        return Logger(name)

    @staticmethod
    def _ConfigureLogging(
        *args: Tuple[Any, ...],
        logger: logging.Logger,
        level: LoggerLevel,
        target: LoggerTarget,
        format: Optional[str] = None,
        datefmt: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> None:
        handler: logging.Handler = TARGET_HANDLER_MAP.get(target, DEFAULT_HANDLER)(*args, **kwargs)  # type: ignore
        formatter = logging.Formatter(format or DEFAULT_FORMAT, datefmt=datefmt or DEFAULT_DATEFMT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level.value)
