from MiravejaCore.Gallery.Application.GenerateThumbnail import GenerateThumbnailHandler
from MiravejaCore.Gallery.Infrastructure.GalleryDependencies import AddThumbnailToImageMetadataHandler
from MiravejaCore.Gallery.Infrastructure.GalleryDependencies import GalleryDependencies as GalleryDependenciesBase
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Application.EventDispatcher import ILogger

from MiravejaWorker.Gallery.Subscribers.WhenImageMetadataRegistered.GenerateImageThumbnail import (
    GenerateImageThumbnail,
    IImageContentProvider,
)


class GalleryDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        GalleryDependenciesBase.RegisterDependencies(container)
        container.RegisterFactories(
            {
                GenerateImageThumbnail.__name__: lambda container: GenerateImageThumbnail(
                    logger=container.Get(ILogger.__name__),
                    generateThumbnailHandler=container.Get(GenerateThumbnailHandler.__name__),
                    addThumbnailToImageMetadataHandler=container.Get(AddThumbnailToImageMetadataHandler.__name__),
                    imageContentProvider=container.Get(IImageContentProvider.__name__),
                ),
            }
        )
