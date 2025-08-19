"""
Dependencies for Storage context
"""

from src.Core.DI.Container import Container
from src.Core.Logging.Logger import Logger
from src.Storage.Application.Handlers import *
from src.Storage.Domain.Interfaces import IEncryptionService, IImageRepository, IProviderRepository, IImageContentRepository
from src.Storage.Infrastructure.Repositories import SqlImageRepository, SqlProviderRepository, FilesystemImageContentRepository
from src.Storage.Infrastructure.Encryption import AES256EncryptionService
from src.Storage.Infrastructure.Http.Controller import StorageController
from sqlalchemy.orm import Session as DatabaseSession

class StorageDependencies:
    @staticmethod
    def register_dependencies(container: Container):
        container.register_factories(
            {
                # Services
                IEncryptionService.__name__: lambda container: AES256EncryptionService(container.get("encryption_secret")),
                # Repositories
                IImageRepository.__name__: lambda container: SqlImageRepository(container.get(DatabaseSession.__name__)),
                IProviderRepository.__name__: lambda container: SqlProviderRepository(container.get(DatabaseSession.__name__)),
                IImageContentRepository.__name__: lambda container: FilesystemImageContentRepository(container.get(IEncryptionService.__name__), container.get("filesystem_path"), container.get("final_extension")),
                # Handlers
                RegisterImageHandler.__name__: lambda container: RegisterImageHandler(
                    image_repository=container.get(IImageRepository.__name__),
                    logger=container.get(Logger.__name__)
                ),
                ListAllImagesHandler.__name__: lambda container: ListAllImagesHandler(
                    image_repository=container.get(IImageRepository.__name__),
                    logger=container.get(Logger.__name__)
                ),
                FindImageByIdHandler.__name__: lambda container: FindImageByIdHandler(
                    image_repository=container.get(IImageRepository.__name__),
                    logger=container.get(Logger.__name__)
                ),
                RegisterProviderHandler.__name__: lambda container: RegisterProviderHandler(
                    provider_repository=container.get(IProviderRepository.__name__),
                    logger=container.get(Logger.__name__)
                ),
                ListAllProvidersHandler.__name__: lambda container: ListAllProvidersHandler(
                    provider_repository=container.get(IProviderRepository.__name__),
                    logger=container.get(Logger.__name__)
                ),
                FindProviderByIdHandler.__name__: lambda container: FindProviderByIdHandler(
                    provider_repository=container.get(IProviderRepository.__name__),
                    logger=container.get(Logger.__name__)
                ),
                DownloadImageContentHandler.__name__: lambda container: DownloadImageContentHandler(
                    image_content_repository=container.get(IImageContentRepository.__name__),
                    image_repository=container.get(IImageRepository.__name__),
                    logger=container.get(Logger.__name__)
                ),
                UploadImageContentHandler.__name__: lambda container: UploadImageContentHandler(
                    image_content_repository=container.get(IImageContentRepository.__name__),
                    logger=container.get(Logger.__name__)
                ),
                # Controller
                StorageController.__name__: lambda container: StorageController(
                    register_image_handler=container.get(RegisterImageHandler.__name__),
                    list_all_images_handler=container.get(ListAllImagesHandler.__name__),
                    find_image_by_id_handler=container.get(FindImageByIdHandler.__name__),
                    register_provider_handler=container.get(RegisterProviderHandler.__name__),
                    list_all_providers_handler=container.get(ListAllProvidersHandler.__name__),
                    find_provider_by_id_handler=container.get(FindProviderByIdHandler.__name__),
                    upload_image_content_handler=container.get(UploadImageContentHandler.__name__),
                    download_image_content_handler=container.get(DownloadImageContentHandler.__name__),
                    logger=container.get(Logger.__name__)
                )
            }
        )
