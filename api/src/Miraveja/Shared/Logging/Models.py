import logging
from typing import Tuple, Dict, Any
from logging import Formatter, Handler, StreamHandler
from Miraveja.Shared.Logging.Interfaces import ILogger


class Logger(ILogger):
    def __init__(self, name: str = "miraveja"):
        self._logger = logging.getLogger(name)
        if not self._logger.handlers:
            # Basic console handler
            handler: Handler = StreamHandler()
            formatter: Formatter = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def Debug(self, msg: str, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        self._logger.debug(msg, *args, **kwargs)  # type: ignore

    def Info(self, msg: str, *args: Tuple[Any], **kwargs: Dict[str, Any]):
        self._logger.info(msg, *args, **kwargs)  # type: ignore

    def Warning(self, msg: str, *args: Tuple[Any], **kwargs: Dict[str, Any]):
        self._logger.warning(msg, *args, **kwargs)  # type: ignore

    def Error(self, msg: str, *args: Tuple[Any], **kwargs: Dict[str, Any]):
        self._logger.error(msg, *args, **kwargs)  # type: ignore

    def Critical(self, msg: str, *args: Tuple[Any], **kwargs: Dict[str, Any]):
        self._logger.critical(msg, *args, **kwargs)  # type: ignore
