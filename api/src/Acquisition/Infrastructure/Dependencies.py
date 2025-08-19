"""
Dependencies for Acquisition context
"""

from src.Core.DI.Container import Container
from src.Core.Events.Bus import EventDispatcher
from src.Core.Logging.Logger import Logger
from src.Core.Tasks.TaskManager import TaskManager
from src.Acquisition.Application.Handlers import *
from src.Acquisition.Domain.Interfaces import IImageDownloader, IImageProvider, IStorageService
from src.Acquisition.Domain.Services import ImageAcquisitionService
from src.Acquisition.Infrastructure.ImageDownloader import ImageDownloader
from src.Acquisition.Infrastructure.ImageProvider import CivitaiImageProvider
from src.Acquisition.Infrastructure.InternalSevices import InternalStorageService
from src.Acquisition.Infrastructure.Http.Controller import AcquisitionController
from src.Storage.Application.Handlers import RegisterImageHandler, UploadImageContentHandler
from src.Config.AppConfig import AppConfig

class AcquisitionDependencies:
    @staticmethod
    def register_dependencies(container: Container):
        container.register_factories(
            {
                # Services
                IStorageService.__name__ : lambda container: InternalStorageService(
                    upload_image_content_handler=container.get(UploadImageContentHandler.__name__),
                    register_image_handler=container.get(RegisterImageHandler.__name__)
                ),
                IImageProvider.__name__ : lambda container: CivitaiImageProvider(
                    config=container.get(AppConfig.__name__).provider_configuration
                ),
                IImageDownloader.__name__ : lambda container: ImageDownloader(),
                ImageAcquisitionService.__name__ : lambda container: ImageAcquisitionService(
                    image_provider=container.get(IImageProvider.__name__),
                    image_downloader=container.get(IImageDownloader.__name__)
                ),
                # Handlers
                AcquireImageHandler.__name__ : lambda container: AcquireImageHandler(
                    image_acquisition_service=container.get(ImageAcquisitionService.__name__),
                    storage_service=container.get(IStorageService.__name__),
                    event_dispatcher=container.get(EventDispatcher.__name__),
                    task_manager=container.get(TaskManager.__name__),
                    logger=container.get(Logger.__name__)
                ),
                # Controller
                AcquisitionController.__name__ : lambda container: AcquisitionController(
                    acquire_image_handler=container.get(AcquireImageHandler.__name__),
                    logger=container.get(Logger.__name__)
                )
            }
        )