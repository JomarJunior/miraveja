from MiravejaCore.Gallery.Application.FindImageMetadataById import FindImageMetadataByIdHandler
from MiravejaCore.Gallery.Application.FindLoraMetadataByHash import FindLoraMetadataByHashHandler
from MiravejaCore.Gallery.Application.GetPresignedPostUrl import GetPresignedPostUrlHandler
from MiravejaCore.Gallery.Application.ListAllImageMetadatas import ListAllImageMetadatasHandler
from MiravejaCore.Gallery.Application.RegisterImageMetadata import (
    RegisterGenerationMetadataHandler,
    RegisterImageMetadataHandler,
)
from MiravejaCore.Gallery.Application.RegisterLoraMetadata import RegisterLoraMetadataHandler
from MiravejaCore.Gallery.Application.UpdateImageMetadata import UpdateImageMetadataHandler
from MiravejaCore.Gallery.Domain.Interfaces import (
    IGenerationMetadataRepository,
    IImageContentRepository,
    IImageMetadataRepository,
    ILoraMetadataRepository,
)
from MiravejaApi.Gallery.Infrastructure.Http.GalleryController import GalleryController
from MiravejaApi.Gallery.Infrastructure.MinIo.Repository import MinIoImageContentRepository
from MiravejaApi.Gallery.Infrastructure.Sql.Repository import (
    SqlGenerationMetadataRepository,
    SqlImageMetadataRepository,
    SqlLoraMetadataRepository,
)
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Shared.Storage.Domain.Services import SignedUrlService
from MiravejaCore.Shared.DatabaseManager.Infrastructure.Factories import SqlDatabaseManagerFactory
from boto3 import Session as Boto3Session


class GalleryDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        container.RegisterFactories(
            {
                # Services
                SignedUrlService.__name__: lambda container: SignedUrlService(
                    config=MinIoConfig.model_validate(container.Get("minIoConfig")),
                ),
                # Repositories
                IImageMetadataRepository.__name__: lambda container: SqlImageMetadataRepository,
                IGenerationMetadataRepository.__name__: lambda container: SqlGenerationMetadataRepository,
                ILoraMetadataRepository.__name__: lambda container: SqlLoraMetadataRepository,
                IImageContentRepository.__name__: lambda container: MinIoImageContentRepository(
                    boto3Client=container.Get(Boto3Session.client.__name__),
                    config=MinIoConfig.model_validate(container.Get("minIoConfig")),
                    logger=container.Get(ILogger.__name__),
                ),
                # Handlers
                FindLoraMetadataByHashHandler.__name__: lambda container: FindLoraMetadataByHashHandler(
                    databaseManagerFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tLoraMetadataRepository=container.Get(ILoraMetadataRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                RegisterLoraMetadataHandler.__name__: lambda container: RegisterLoraMetadataHandler(
                    databaseManagerFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tLoraMetadataRepository=container.Get(ILoraMetadataRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                RegisterGenerationMetadataHandler.__name__: lambda container: RegisterGenerationMetadataHandler(
                    databaseManagerFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tGenerationMetadataRepository=container.Get(IGenerationMetadataRepository.__name__),
                    registerLoraMetadataHandler=container.Get(RegisterLoraMetadataHandler.__name__),
                    findLoraMetadataByHashHandler=container.Get(FindLoraMetadataByHashHandler.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                ListAllImageMetadatasHandler.__name__: lambda container: ListAllImageMetadatasHandler(
                    databaseManagerFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tImageMetadataRepository=container.Get(IImageMetadataRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                FindImageMetadataByIdHandler.__name__: lambda container: FindImageMetadataByIdHandler(
                    databaseManagerFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tImageMetadataRepository=container.Get(IImageMetadataRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                RegisterImageMetadataHandler.__name__: lambda container: RegisterImageMetadataHandler(
                    databaseManagerFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tImageMetadataRepository=container.Get(IImageMetadataRepository.__name__),
                    registerGenerationMetadataHandler=container.Get(RegisterGenerationMetadataHandler.__name__),
                    imageContentRepository=container.Get(IImageContentRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                ),
                UpdateImageMetadataHandler.__name__: lambda container: UpdateImageMetadataHandler(
                    databaseManagerFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tImageMetadataRepository=container.Get(IImageMetadataRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                ),
                GetPresignedPostUrlHandler.__name__: lambda container: GetPresignedPostUrlHandler(
                    imageContentRepository=container.Get(IImageContentRepository.__name__),
                    signedUrlService=container.Get(SignedUrlService.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                # Controllers
                GalleryController.__name__: lambda container: GalleryController(
                    listAllImageMetadatasHandler=container.Get(ListAllImageMetadatasHandler.__name__),
                    findImageMetadataByIdHandler=container.Get(FindImageMetadataByIdHandler.__name__),
                    registerImageMetadataHandler=container.Get(RegisterImageMetadataHandler.__name__),
                    updateImageMetadataHandler=container.Get(UpdateImageMetadataHandler.__name__),
                    getPresignedPostUrlHandler=container.Get(GetPresignedPostUrlHandler.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
