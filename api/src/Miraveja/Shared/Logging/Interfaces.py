from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any


class ILogger(ABC):
    @abstractmethod
    def Debug(self, msg: str, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        pass

    @abstractmethod
    def Info(self, msg: str, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        pass

    @abstractmethod
    def Warning(self, msg: str, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        pass

    @abstractmethod
    def Error(self, msg: str, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        pass

    @abstractmethod
    def Critical(self, msg: str, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]):
        pass
