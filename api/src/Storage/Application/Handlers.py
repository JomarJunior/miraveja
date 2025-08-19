"""
Handlers for Storage context Use Cases
"""

from src.Core.Logging.Logger import Logger
from src.Storage.Application.Commands import (
    RegisterImageCommand,
    ListAllImagesCommand,
    FindImageByIdCommand,
    RegisterProviderCommand,
    ListAllProvidersCommand,
    FindProviderByIdCommand,
    DownloadImageContentCommand,
    UploadImageContentCommand,
)
from src.Storage.Domain.Interfaces import IImageRepository, IProviderRepository, IImageContentRepository
from src.Storage.Domain.Models import Image, Provider, ImageContent
from src.Storage.Domain.Enums import ImageFormatEnum
from typing import Any, Dict

# Images
class ListAllImagesHandler:
    def __init__(self, image_repository: IImageRepository, logger: Logger):
        self.image_repository = image_repository
        self.logger = logger

    def handle(self, command: ListAllImagesCommand) -> list[Dict[str, Any]]:
        self.logger.info(f"Handling ListAllImagesCommand with params: {command}")
        images = self.image_repository.list_all(
            sort_by=command.sort_by,
            sort_order=command.sort_order,
            search_filter=command.search_filter,
            limit=command.limit
        )
        self.logger.info(f"Found {len(images)} images")
        return [image.to_dict() for image in images]

class FindImageByIdHandler:
    def __init__(self, image_repository: IImageRepository, logger: Logger):
        self.image_repository = image_repository
        self.logger = logger

    def handle(self, command: FindImageByIdCommand) -> Dict[str, Any]:
        self.logger.info(f"Handling FindImageByIdCommand with params: {command}")
        image = self.image_repository.find_by_id(command.id)
        self.logger.info(f"Found image: {image}")
        if not image:
            raise KeyError(f"Image with ID {command.id} not found")
        return image.to_dict()

class RegisterImageHandler:
    def __init__(self, image_repository: IImageRepository, logger: Logger):
        self.image_repository = image_repository
        self.logger = logger

    def handle(self, command: RegisterImageCommand) -> int:
        """
        Handle the registration of a new image. Returns the ID of the registered image.
        """
        self.logger.info(f"Handling RegisterImageCommand with params: {command}")
        try:
            existing_image = self.image_repository.find_by_uri(command.image_uri)
            if existing_image:
                self.logger.info(f"Image already exists: {existing_image.uri}")
                return existing_image.id
        except KeyError:
            self.logger.info(f"Image does not exist, creating...")

        image = Image(
            uri=command.image_uri,
            image_metadata=command.image_metadata,
            provider_id=command.provider_id
        )
        self.image_repository.save(image)
        self.logger.info(f"Registered image: {image}")
        return image.id

# Providers
class ListAllProvidersHandler:
    def __init__(self, provider_repository: IProviderRepository, logger: Logger):
        self.provider_repository = provider_repository
        self.logger = logger

    def handle(self, command: ListAllProvidersCommand) -> list[Dict[str, Any]]:
        self.logger.info(f"Handling ListAllProvidersCommand with params: {command}")
        providers = self.provider_repository.list_all(
            sort_by=command.sort_by,
            sort_order=command.sort_order,
            search_filter=command.search_filter,
            limit=command.limit
        )
        self.logger.info(f"Found {len(providers)} providers")
        return [provider.to_dict() for provider in providers]

class FindProviderByIdHandler:
    def __init__(self, provider_repository: IProviderRepository, logger: Logger):
        self.provider_repository = provider_repository
        self.logger = logger

    def handle(self, command: FindProviderByIdCommand) -> Dict[str, Any]:
        self.logger.info(f"Handling FindProviderByIdCommand with params: {command}")
        provider = self.provider_repository.find_by_id(command.id)
        self.logger.info(f"Found provider: {provider}")
        if not provider:
            raise KeyError(f"Provider with ID {command.id} not found")
        return provider.to_dict()

class RegisterProviderHandler:
    def __init__(self, provider_repository: IProviderRepository, logger: Logger):
        self.provider_repository = provider_repository
        self.logger = logger

    def handle(self, command: RegisterProviderCommand) -> None:
        self.logger.info(f"Handling RegisterProviderCommand with params: {command}")
        provider = Provider(
            name=command.name
        )
        self.provider_repository.save(provider)
        self.logger.info(f"Registered provider: {provider}")

# Image Content
class DownloadImageContentHandler:
    def __init__(self, image_content_repository: IImageContentRepository, image_repository: IImageRepository, logger: Logger):
        self.image_content_repository = image_content_repository
        self.image_repository = image_repository
        self.logger = logger

    def handle(self, command: DownloadImageContentCommand) -> Dict[str, Any]:
        self.logger.info(f"Handling DownloadImageContentCommand with params: {command}")

        # Fetch the image from the database
        image: Image = self.image_repository.find_by_id(command.id)
        if not image:
            raise KeyError(f"Image with ID {command.id} not found")

        # Retrieve the contents of the fetched image
        image_content: ImageContent = self.image_content_repository.find_by_uri(image.uri)
        if not image_content:
            raise KeyError(f"Image content with URI {image.uri} not found")
        return {"content": image_content.get_bytes_content(), "mime_type": image_content.get_format().to_mime_type()}
    
class UploadImageContentHandler:
    def __init__(self, image_content_repository: IImageContentRepository, logger: Logger):
        self.image_content_repository = image_content_repository
        self.logger = logger

    def handle(self, command: UploadImageContentCommand) -> str:
        """
        Handle the upload of image content. Returns the URI of the uploaded content.
        """
        self.logger.info(f"Handling UploadImageContentCommand with params: {command}")

        # Check if the content already exists
        try:
            already_existing_content = self.image_content_repository.find_by_content(command.content)
            self.logger.info(f"Content already exists, returning existing URI: {already_existing_content.uri}")
            return already_existing_content.uri
        except KeyError:
            self.logger.info(f"Content does not exist, creating...")

        # If the content is new, create a new entry
        base64_prefix: str = command.content.split(";")[0]
        extension: str = ImageFormatEnum(base64_prefix)
        self.logger.info(f"Detected image format: {extension}")

        new_uri: str = self.image_content_repository.get_next_available_uri(extension.to_extension())
        self.logger.info(f"Generated new URI for image content: {new_uri}")

        new_image_content: ImageContent = ImageContent.create(
            uri=new_uri,
            content=command.content
        )
        self.logger.info(f"Saving new image content...")

        self.image_content_repository.save(new_image_content)
        self.logger.info(f"Uploaded image content: {new_image_content}")
        return new_uri
