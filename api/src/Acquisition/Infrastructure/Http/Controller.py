"""
Controller for Acquisition context
"""

from src.Acquisition.Application.Commands import (
    AcquireImageCommand
)
from src.Acquisition.Application.Handlers import (
    AcquireImageHandler
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

class AcquisitionController:

    def __init__(
            self,
            acquire_image_handler: AcquireImageHandler,
            logger: Logger
    ):

        self.acquire_image_handler = acquire_image_handler
        self.logger = logger

    def acquire_images(self, request: Request) -> Response:
        try:
            command = AcquireImageCommand.from_dict(request.get_json(silent=True) or {})
            result = self.acquire_image_handler.handle(command)
            return Response(status=ErrorCodes.SUCCESS, response=json.dumps(result), mimetype=MimeTypes.JSON)
        except Exception as e:
            return self.handle_error(e)

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