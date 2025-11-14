import httpx
from MiravejaCore.Shared.DI.Models import Container

from MiravejaWorker.Shared.Storage.Domain.Interfaces import IImageContentProvider
from MiravejaWorker.Shared.Storage.Infrastructure.Http.Providers import HttpImageContentProvider


class StorageDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        container.RegisterFactories(
            {
                HttpImageContentProvider.__name__: lambda container: HttpImageContentProvider(
                    httpClient=container.Get(httpx.AsyncClient.__name__),
                ),
                IImageContentProvider.__name__: lambda container: container.Get(HttpImageContentProvider.__name__),
            }
        )
