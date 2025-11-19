from MiravejaCore.Gallery.Application.FindImageMetadataById import FindImageMetadataByIdHandler
from MiravejaCore.Gallery.Application.FindImageMetadataByVectorId import FindImageMetadataByVectorIdHandler
from MiravejaCore.Gallery.Application.GetPresignedPostUrl import GetPresignedPostUrlHandler
from MiravejaCore.Gallery.Application.ListAllImageMetadatas import ListAllImageMetadatasHandler
from MiravejaCore.Gallery.Application.RegisterImageMetadata import RegisterImageMetadataHandler
from MiravejaCore.Gallery.Application.UpdateImageMetadata import UpdateImageMetadataHandler
from MiravejaCore.Gallery.Infrastructure.GalleryDependencies import GalleryDependencies as GalleryDependenciesBase
from MiravejaCore.Shared.DI import Container
from MiravejaCore.Shared.Logging.Interfaces import ILogger

from MiravejaApi.Gallery.Infrastructure.Http.GalleryController import GalleryController


class GalleryDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        GalleryDependenciesBase.RegisterDependencies(container)
        container.RegisterFactories(
            {
                # Controllers
                GalleryController.__name__: lambda container: GalleryController(
                    listAllImageMetadatasHandler=container.Get(ListAllImageMetadatasHandler.__name__),
                    findImageMetadataByIdHandler=container.Get(FindImageMetadataByIdHandler.__name__),
                    registerImageMetadataHandler=container.Get(RegisterImageMetadataHandler.__name__),
                    updateImageMetadataHandler=container.Get(UpdateImageMetadataHandler.__name__),
                    getPresignedPostUrlHandler=container.Get(GetPresignedPostUrlHandler.__name__),
                    findImageMetadataByVectorIdHandler=container.Get(FindImageMetadataByVectorIdHandler.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
