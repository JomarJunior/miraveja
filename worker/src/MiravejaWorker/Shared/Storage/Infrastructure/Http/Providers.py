import httpx

from MiravejaWorker.Shared.Storage.Domain.Interfaces import IImageContentProvider


class HttpImageContentProvider(IImageContentProvider):
    def __init__(
        self,
        httpClient: httpx.AsyncClient,
    ):
        self._httpClient = httpClient

    async def GetImageContentFromUri(self, uri: str) -> bytes:
        response = await self._httpClient.get(uri)
        response.raise_for_status()
        return response.content
