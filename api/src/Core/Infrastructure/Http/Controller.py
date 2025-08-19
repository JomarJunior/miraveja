"""
Core HTTP Controller
"""

from src.Core.Tasks.TaskManager import TaskManager, TaskResult
from src.Core.Logging.Logger import Logger
from typing import Callable, Optional
from enum import Enum, IntEnum
from flask import Request, Response
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

class CoreController:
    def __init__(self, task_manager: TaskManager, logger: Logger):
        self.task_manager = task_manager
        self.logger = logger

    def get_task_status(self, request: Request, task_id: str) -> Response:
        try:
            task_result = self.task_manager.get_task_status(task_id)
            if not task_result:
                return Response(
                    status=ErrorCodes.NOT_FOUND,
                    response=json.dumps({"error": f"Task with ID {task_id} not found."}),
                    mimetype=MimeTypes.JSON
                )
            return Response(
                status=ErrorCodes.SUCCESS,
                response=json.dumps(task_result.to_dict()),
                mimetype=MimeTypes.JSON
            )
        except Exception as error:
            return self.handle_error(error)

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
