from abc import ABC, abstractmethod


class IImageContentProvider(ABC):
    @abstractmethod
    async def GetImageContentFromUri(self, uri: str) -> bytes:
        pass
