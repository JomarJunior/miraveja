import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from MiravejaCore.Shared.Errors.Models import DomainException
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, logger: ILogger) -> None:  # type: ignore
        super().__init__(app)  # type: ignore
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:  # type: ignore
        # Log request information
        startTime = time.time()

        # Extract request details
        method = request.method
        url = str(request.url)
        headers = dict(request.headers)
        clientIp = request.client.host if request.client else "unknown"
        queryParams = dict(request.query_params)

        self.logger.Info(f"Request: {method} {url} from {clientIp}")
        self.logger.Debug(f"Request headers: {json.dumps(headers, indent=2)}")
        if queryParams:
            self.logger.Debug(f"Query parameters: {json.dumps(queryParams, indent=2)}")

        # Process request
        response = await call_next(request)  # type: ignore

        # Log response information
        processTime = time.time() - startTime
        statusCode = response.status_code  # type: ignore

        self.logger.Info(f"Response: {statusCode} for {method} {url} - {processTime:.3f}s")

        # Add process time to response headers
        response.headers["X-Process-Time"] = str(processTime)  # type: ignore

        return response  # type: ignore


class ErrorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable, logger: ILogger) -> None:  # type: ignore
        super().__init__(app)  # type: ignore
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:  # type: ignore
        try:
            response = await call_next(request)  # type: ignore
            return response  # type: ignore
        except DomainException as de:
            self.logger.Error(f"Domain exception: {str(de)}", exc_info=True)  # type: ignore
            return Response(str(de), status_code=400)  # type: ignore
        except Exception as e:
            self.logger.Error(f"Unhandled exception: {str(e)}", exc_info=True)  # type: ignore
            return Response("Internal server error", status_code=500)  # type: ignore
