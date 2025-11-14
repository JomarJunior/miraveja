import httpx
from MiravejaCore.Gallery.Application.AddVectorIdToImageMetadata import AddVectorIdToImageMetadataHandler
from MiravejaCore.Shared.DI import Container
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Vector.Application.GenerateImageVector import GenerateImageVectorHandler
from MiravejaCore.Vector.Infrastructure.VectorDependencies import VectorDependencies as VectorDependenciesBase

from MiravejaWorker.Shared.Storage.Domain.Interfaces import IImageContentProvider
from MiravejaWorker.Vector.Subscribers.WhenImageMetadataRegistered.GenerateImageVector import (
    GenerateImageVector,
)


class VectorDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        VectorDependenciesBase.RegisterDependencies(container)
        container.RegisterFactories(
            {
                GenerateImageVector.__name__: lambda container: GenerateImageVector(
                    logger=container.Get(ILogger.__name__),
                    generateImageVectorHandler=container.Get(GenerateImageVectorHandler.__name__),
                    addVectorIdToImageMetadataHandler=container.Get(AddVectorIdToImageMetadataHandler.__name__),
                    imageContentProvider=container.Get(IImageContentProvider.__name__),
                ),
            }
        )
