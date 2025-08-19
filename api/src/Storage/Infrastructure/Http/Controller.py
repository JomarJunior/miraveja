"""
Controller for Storage context
"""

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
from src.Storage.Application.Handlers import (
    RegisterImageHandler,
    ListAllImagesHandler,
    FindImageByIdHandler,
    RegisterProviderHandler,
    ListAllProvidersHandler,
    FindProviderByIdHandler,
    DownloadImageContentHandler,
    UploadImageContentHandler,
)
from src.Core.Logging.Logger import Logger
from flask import Request, Response
from enum import Enum, IntEnum
import json
from random import randbytes

class ErrorCodes(IntEnum):
    SUCCESS = 200
    SUCCESS_NO_CONTENT = 204
    BAD_REQUEST = 400
    NOT_FOUND = 404
    FORBIDDEN = 403
    INTERNAL_SERVER_ERROR = 500
    I_AM_A_TEAPOT = 418  # Very important

class MimeTypes(str, Enum):
    JSON = "application/json"
    PNG = "image/png"
    JPEG = "image/jpeg"
    GIF = "image/gif"

    def __str__(self):
        return self.value


class StorageController:
    def __init__(
            self,
            register_image_handler: RegisterImageHandler,
            list_all_images_handler: ListAllImagesHandler,
            find_image_by_id_handler: FindImageByIdHandler,
            register_provider_handler: RegisterProviderHandler,
            list_all_providers_handler: ListAllProvidersHandler,
            find_provider_by_id_handler: FindProviderByIdHandler,
            download_image_content_handler: DownloadImageContentHandler,
            upload_image_content_handler: UploadImageContentHandler,
            logger: Logger,
    ):
        self.register_image_handler = register_image_handler
        self.list_all_images_handler = list_all_images_handler
        self.find_image_by_id_handler = find_image_by_id_handler
        self.register_provider_handler = register_provider_handler
        self.list_all_providers_handler = list_all_providers_handler
        self.find_provider_by_id_handler = find_provider_by_id_handler
        self.download_image_content_handler = download_image_content_handler
        self.upload_image_content_handler = upload_image_content_handler
        self.logger = logger

    # Images
    def list_all_images(self, request: Request) -> Response:
        try:
            command = ListAllImagesCommand.from_dict(request.args.to_dict())
            images = self.list_all_images_handler.handle(command)
        except Exception as e:
            return self.handle_error(e)
        return Response(response=json.dumps(images), status=ErrorCodes.SUCCESS, mimetype=MimeTypes.JSON)

    def find_image_by_id(self, request: Request, image_id: int) -> Response:
        try:
            command = FindImageByIdCommand.from_dict({"id": image_id})
            image = self.find_image_by_id_handler.handle(command)
        except Exception as e:
            return self.handle_error(e)
        return Response(response=json.dumps(image), status=ErrorCodes.SUCCESS, mimetype=MimeTypes.JSON)

    def register_image(self, request: Request) -> Response:
        try:
            command = RegisterImageCommand.from_dict(request.get_json())
            image_id: int = self.register_image_handler.handle(command)
        except Exception as e:
            return self.handle_error(e)
        return Response(response=json.dumps({"id": image_id}), status=ErrorCodes.SUCCESS, mimetype=MimeTypes.JSON)

    # Providers
    def list_all_providers(self, request: Request) -> Response:
        try:
            command = ListAllProvidersCommand.from_dict(request.args.to_dict())
            providers = self.list_all_providers_handler.handle(command)
        except Exception as e:
            return self.handle_error(e)
        return Response(response=json.dumps(providers), status=ErrorCodes.SUCCESS, mimetype=MimeTypes.JSON)

    def find_provider_by_id(self, request: Request, provider_id: int) -> Response:
        try:
            command = FindProviderByIdCommand.from_dict({"id": provider_id})
            provider = self.find_provider_by_id_handler.handle(command)
        except Exception as e:
            return self.handle_error(e)
        return Response(response=json.dumps(provider), status=ErrorCodes.SUCCESS, mimetype=MimeTypes.JSON)

    def register_provider(self, request: Request) -> Response:
        try:
            command = RegisterProviderCommand.from_dict(request.get_json())
            self.register_provider_handler.handle(command)
        except Exception as e:
            return self.handle_error(e)
        return Response(status=ErrorCodes.SUCCESS_NO_CONTENT)
    
    # Image Content
    def download_image_content(self, request: Request, id: int) -> Response:
        try:
            command = DownloadImageContentCommand(id)
            image_content = self.download_image_content_handler.handle(command)
        except Exception as e:
            return self.handle_error(e)
        return Response(response=image_content["content"], status=ErrorCodes.SUCCESS, mimetype=MimeTypes(image_content["mime_type"]))

    def upload_image_content(self, request: Request) -> Response:
        try:
            command = UploadImageContentCommand.from_dict(request.get_json())
            new_uri = self.upload_image_content_handler.handle(command)
        except Exception as e:
            return self.handle_error(e)
        return Response(response=json.dumps({"uri": new_uri}), status=ErrorCodes.SUCCESS, mimetype=MimeTypes.JSON)

    # Error handling
    def handle_error(self, error: Exception) -> Response:
        hex_code: str = f"0x{randbytes(16).hex()}"
        self.logger.error(f"Error occurred: {error}")
        self.logger.error(f"Error code: {hex_code}")
        if (isinstance(error, ValueError) or isinstance(error, TypeError)):
            return Response(status=ErrorCodes.BAD_REQUEST, response=json.dumps({"error": str(error)}), mimetype=MimeTypes.JSON)
        if (isinstance(error, KeyError)):
            return Response(status=ErrorCodes.NOT_FOUND, response=json.dumps({"error": str(error)}), mimetype=MimeTypes.JSON)
        if (isinstance(error, PermissionError)):
            return Response(status=ErrorCodes.FORBIDDEN, response=json.dumps({"error": str(error)}), mimetype=MimeTypes.JSON)
        return Response(
            status=ErrorCodes.INTERNAL_SERVER_ERROR,
            response=json.dumps({"error": f"An internal server error occurred. Reference code: {hex_code}"}),
            mimetype=MimeTypes.JSON
        )