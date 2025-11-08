"""Unit tests for GalleryDependencies module."""

from unittest.mock import MagicMock, patch

import pytest

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
from MiravejaCore.Gallery.Infrastructure.GalleryDependencies import GalleryDependencies
from MiravejaCore.Gallery.Infrastructure.MinIo.Repository import MinIoImageContentRepository
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.DatabaseManager.Infrastructure.Factories import SqlDatabaseManagerFactory
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Shared.Storage.Domain.Services import SignedUrlService
from boto3 import Session as Boto3Session


class TestGalleryDependencies:
    """Test cases for GalleryDependencies configuration."""

    def test_RegisterDependencies_ShouldRegisterSignedUrlService(self):
        """Test that RegisterDependencies registers SignedUrlService as factory."""
        container = Container()

        # Setup mock dependencies
        mock_minio_config = {
            "endpoint": "localhost:9000",
            "accessKey": "minioadmin",
            "secretKey": "minioadmin",
            "secure": False,
            "region": "us-east-1",
            "bucketName": "test-bucket",
        }
        container.instances["minioConfig"] = mock_minio_config

        # Register dependencies
        GalleryDependencies.RegisterDependencies(container)

        # Verify SignedUrlService is registered
        service = container.Get(SignedUrlService.__name__)
        assert service is not None
        assert isinstance(service, SignedUrlService)

    def test_RegisterDependencies_ShouldRegisterRepositories(self):
        """Test that RegisterDependencies registers all repository interfaces."""
        container = Container()

        # Setup mock dependencies
        container.instances["minioConfig"] = {
            "endpoint": "localhost:9000",
            "accessKey": "minioadmin",
            "secretKey": "minioadmin",
            "secure": False,
            "region": "us-east-1",
            "bucketName": "test-bucket",
        }
        mock_boto3_client = MagicMock()
        mock_logger = MagicMock(spec=ILogger)
        container.instances[Boto3Session.client.__name__] = mock_boto3_client
        container.instances[ILogger.__name__] = mock_logger

        # Register dependencies
        GalleryDependencies.RegisterDependencies(container)

        # Verify repositories are registered
        assert container.Get(IImageMetadataRepository.__name__) is not None
        assert container.Get(IGenerationMetadataRepository.__name__) is not None
        assert container.Get(ILoraMetadataRepository.__name__) is not None

        # Verify ImageContentRepository is MinIo implementation
        image_content_repo = container.Get(IImageContentRepository.__name__)
        assert image_content_repo is not None
        assert isinstance(image_content_repo, MinIoImageContentRepository)

    def test_RegisterDependencies_ShouldRegisterApplicationHandlers(self):
        """Test that RegisterDependencies registers all application handlers."""
        container = Container()

        # Setup mock dependencies
        container.instances["minioConfig"] = {
            "endpoint": "localhost:9000",
            "accessKey": "minioadmin",
            "secretKey": "minioadmin",
            "secure": False,
            "region": "us-east-1",
            "bucketName": "test-bucket",
        }
        container.instances[ILogger.__name__] = MagicMock(spec=ILogger)
        container.instances[Boto3Session.client.__name__] = MagicMock()
        container.instances[SqlDatabaseManagerFactory.__name__] = MagicMock()
        container.instances[EventDispatcher.__name__] = MagicMock(spec=EventDispatcher)

        # Register dependencies
        GalleryDependencies.RegisterDependencies(container)

        # Verify all handlers are registered
        assert container.Get(FindLoraMetadataByHashHandler.__name__) is not None
        assert container.Get(RegisterLoraMetadataHandler.__name__) is not None
        assert container.Get(RegisterGenerationMetadataHandler.__name__) is not None
        assert container.Get(ListAllImageMetadatasHandler.__name__) is not None
        assert container.Get(FindImageMetadataByIdHandler.__name__) is not None
        assert container.Get(RegisterImageMetadataHandler.__name__) is not None
        assert container.Get(UpdateImageMetadataHandler.__name__) is not None
        assert container.Get(GetPresignedPostUrlHandler.__name__) is not None

    def test_RegisterDependencies_FindLoraMetadataByHashHandler_ShouldInjectDependencies(self):
        """Test that FindLoraMetadataByHashHandler factory injects correct dependencies."""
        container = Container()

        # Setup mock dependencies
        mock_db_factory = MagicMock(spec=SqlDatabaseManagerFactory)
        mock_logger = MagicMock(spec=ILogger)
        container.instances["minioConfig"] = {
            "endpoint": "localhost:9000",
            "accessKey": "test",
            "secretKey": "test",
            "secure": False,
            "region": "us-east-1",
            "bucketName": "bucket",
        }
        container.instances[ILogger.__name__] = mock_logger
        container.instances[SqlDatabaseManagerFactory.__name__] = mock_db_factory
        container.instances[Boto3Session.client.__name__] = MagicMock()

        # Register dependencies
        GalleryDependencies.RegisterDependencies(container)

        # Get handler and verify dependencies
        handler = container.Get(FindLoraMetadataByHashHandler.__name__)
        assert handler._databaseManagerFactory == mock_db_factory
        assert handler._logger == mock_logger

    def test_RegisterDependencies_RegisterImageMetadataHandler_ShouldInjectAllDependencies(self):
        """Test that RegisterImageMetadataHandler factory injects all dependencies including nested handlers."""
        container = Container()

        # Setup mock dependencies
        mock_db_factory = MagicMock(spec=SqlDatabaseManagerFactory)
        mock_logger = MagicMock(spec=ILogger)
        mock_event_dispatcher = MagicMock(spec=EventDispatcher)
        container.instances["minioConfig"] = {
            "endpoint": "localhost:9000",
            "accessKey": "test",
            "secretKey": "test",
            "secure": False,
            "region": "us-east-1",
            "bucketName": "bucket",
        }
        container.instances[ILogger.__name__] = mock_logger
        container.instances[SqlDatabaseManagerFactory.__name__] = mock_db_factory
        container.instances[EventDispatcher.__name__] = mock_event_dispatcher
        container.instances[Boto3Session.client.__name__] = MagicMock()

        # Register dependencies
        GalleryDependencies.RegisterDependencies(container)

        # Get handler and verify dependencies
        handler = container.Get(RegisterImageMetadataHandler.__name__)
        assert handler._databaseManagerFactory == mock_db_factory
        assert handler._logger == mock_logger
        assert handler._eventDispatcher == mock_event_dispatcher
        assert handler._registerGenerationMetadataHandler is not None
        assert handler._imageContentRepository is not None

    def test_RegisterDependencies_MinIoImageContentRepository_ShouldUseBoto3Client(self):
        """Test that MinIoImageContentRepository is created with boto3 client."""
        container = Container()

        # Setup mock dependencies
        mock_boto3_client = MagicMock()
        mock_logger = MagicMock(spec=ILogger)
        minio_config_dict = {
            "endpoint": "s3.amazonaws.com",
            "accessKey": "AKIAIOSFODNN7EXAMPLE",
            "secretKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "secure": True,
            "region": "us-west-2",
            "bucketName": "my-bucket",
        }
        container.instances[Boto3Session.client.__name__] = mock_boto3_client
        container.instances[ILogger.__name__] = mock_logger
        container.instances["minioConfig"] = minio_config_dict

        # Register dependencies
        GalleryDependencies.RegisterDependencies(container)

        # Get repository and verify
        repo = container.Get(IImageContentRepository.__name__)
        assert isinstance(repo, MinIoImageContentRepository)
        assert repo._boto3Client == mock_boto3_client

    def test_RegisterDependencies_SignedUrlService_ShouldUseMinIoConfig(self):
        """Test that SignedUrlService uses MinIoConfig from container."""
        container = Container()

        # Setup dependencies with specific config values
        minio_config_dict = {
            "endpoint": "minio.example.com:9000",
            "accessKey": "myaccesskey",
            "secretKey": "mysecretkey",
            "secure": True,
            "region": "eu-central-1",
            "bucketName": "images",
        }
        container.instances["minioConfig"] = minio_config_dict

        # Register dependencies
        GalleryDependencies.RegisterDependencies(container)

        # Get service and verify config was used (config is private, so just verify creation)
        service = container.Get(SignedUrlService.__name__)
        assert service is not None
        assert isinstance(service, SignedUrlService)

    def test_RegisterDependencies_MultipleHandlerInstances_ShouldCreateNewInstances(self):
        """Test that handlers are created as factories (new instance each time)."""
        container = Container()

        # Setup mock dependencies
        container.instances["minioConfig"] = {
            "endpoint": "localhost:9000",
            "accessKey": "test",
            "secretKey": "test",
            "secure": False,
            "region": "us-east-1",
            "bucketName": "bucket",
        }
        container.instances[ILogger.__name__] = MagicMock(spec=ILogger)
        container.instances[SqlDatabaseManagerFactory.__name__] = MagicMock()
        container.instances[EventDispatcher.__name__] = MagicMock()
        container.instances[Boto3Session.client.__name__] = MagicMock()

        # Register dependencies
        GalleryDependencies.RegisterDependencies(container)

        # Get multiple instances of same handler
        handler1 = container.Get(ListAllImageMetadatasHandler.__name__)
        handler2 = container.Get(ListAllImageMetadatasHandler.__name__)

        # Verify they are different instances (factory pattern)
        assert handler1 is not handler2

    def test_RegisterDependencies_GalleryController_ShouldRegisterFactory(self):
        """Test that GalleryController factory is registered and can be retrieved."""
        container = Container()

        # Setup mock dependencies
        container.instances["minioConfig"] = {
            "endpoint": "localhost:9000",
            "accessKey": "test",
            "secretKey": "test",
            "secure": False,
            "region": "us-east-1",
            "bucketName": "bucket",
        }
        container.instances[ILogger.__name__] = MagicMock(spec=ILogger)
        container.instances[SqlDatabaseManagerFactory.__name__] = MagicMock()
        container.instances[EventDispatcher.__name__] = MagicMock()
        container.instances[Boto3Session.client.__name__] = MagicMock()

        # Register dependencies
        GalleryDependencies.RegisterDependencies(container)

        # Get controller - just verify it's registered and creates instance
        from MiravejaApi.Gallery.Infrastructure.Http.GalleryController import GalleryController

        controller = container.Get(GalleryController.__name__)

        # Verify controller was created (we can't easily inspect all dependencies without accessing privates)
        assert controller is not None
        # Just verify it has the expected type
        from MiravejaApi.Gallery.Infrastructure.Http.GalleryController import GalleryController as ControllerClass

        assert isinstance(controller, ControllerClass)
