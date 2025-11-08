"""
Unit tests for Middlewares Models.

Tests RequestResponseLoggingMiddleware and ErrorMiddleware.
"""

import time
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import Request, Response
from starlette.datastructures import Headers, QueryParams

from MiravejaCore.Shared.Errors.Models import DomainException
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Middlewares.Models import (
    RequestResponseLoggingMiddleware,
    ErrorMiddleware,
)


class TestRequestResponseLoggingMiddleware:
    """Tests for RequestResponseLoggingMiddleware."""

    @pytest.mark.asyncio
    async def test_Dispatch_WithValidRequest_ShouldLogRequestAndResponse(self):
        # Arrange
        mockLogger = MagicMock(spec=ILogger)
        mockApp = MagicMock()
        middleware = RequestResponseLoggingMiddleware(app=mockApp, logger=mockLogger)

        # Create mock request
        mockRequest = MagicMock(spec=Request)
        mockRequest.method = "GET"
        mockRequest.url = MagicMock()
        mockRequest.url.__str__ = MagicMock(return_value="http://example.com/api/test")
        mockRequest.headers = Headers({"user-agent": "test-agent", "accept": "*/*"})
        mockRequest.client = MagicMock()
        mockRequest.client.host = "192.168.1.100"
        mockRequest.query_params = QueryParams({"param1": "value1", "param2": "value2"})

        # Create mock response
        mockResponse = MagicMock(spec=Response)
        mockResponse.status_code = 200
        mockResponse.headers = {}

        # Mock call_next
        mockCallNext = AsyncMock(return_value=mockResponse)

        # Act
        with patch("time.time", side_effect=[1000.0, 1000.5]):  # 0.5 second process time
            result = await middleware.dispatch(mockRequest, mockCallNext)

        # Assert
        assert result == mockResponse
        assert mockResponse.headers["X-Process-Time"] == "0.5"

        # Verify logging calls
        assert mockLogger.Info.call_count == 2
        mockLogger.Info.assert_any_call("Request: GET http://example.com/api/test from 192.168.1.100")
        mockLogger.Info.assert_any_call("Response: 200 for GET http://example.com/api/test - 0.500s")

        assert mockLogger.Debug.call_count == 2  # Headers and query params

    @pytest.mark.asyncio
    async def test_Dispatch_WithNoQueryParams_ShouldNotLogQueryParams(self):
        # Arrange
        mockLogger = MagicMock(spec=ILogger)
        mockApp = MagicMock()
        middleware = RequestResponseLoggingMiddleware(app=mockApp, logger=mockLogger)

        # Create mock request without query params
        mockRequest = MagicMock(spec=Request)
        mockRequest.method = "POST"
        mockRequest.url = MagicMock()
        mockRequest.url.__str__ = MagicMock(return_value="http://example.com/api/create")
        mockRequest.headers = Headers({"content-type": "application/json"})
        mockRequest.client = MagicMock()
        mockRequest.client.host = "10.0.0.1"
        mockRequest.query_params = QueryParams()  # Empty query params

        # Create mock response
        mockResponse = MagicMock(spec=Response)
        mockResponse.status_code = 201
        mockResponse.headers = {}

        # Mock call_next
        mockCallNext = AsyncMock(return_value=mockResponse)

        # Act
        with patch("time.time", side_effect=[2000.0, 2000.1]):
            result = await middleware.dispatch(mockRequest, mockCallNext)

        # Assert
        assert result == mockResponse

        # Verify logging - should only have one Debug call for headers, not query params
        assert mockLogger.Debug.call_count == 1

    @pytest.mark.asyncio
    async def test_Dispatch_WithNoClient_ShouldUseUnknownIp(self):
        # Arrange
        mockLogger = MagicMock(spec=ILogger)
        mockApp = MagicMock()
        middleware = RequestResponseLoggingMiddleware(app=mockApp, logger=mockLogger)

        # Create mock request without client
        mockRequest = MagicMock(spec=Request)
        mockRequest.method = "DELETE"
        mockRequest.url = MagicMock()
        mockRequest.url.__str__ = MagicMock(return_value="http://example.com/api/delete/123")
        mockRequest.headers = Headers({})
        mockRequest.client = None  # No client info
        mockRequest.query_params = QueryParams()

        # Create mock response
        mockResponse = MagicMock(spec=Response)
        mockResponse.status_code = 204
        mockResponse.headers = {}

        # Mock call_next
        mockCallNext = AsyncMock(return_value=mockResponse)

        # Act
        with patch("time.time", side_effect=[3000.0, 3000.25]):
            result = await middleware.dispatch(mockRequest, mockCallNext)

        # Assert
        mockLogger.Info.assert_any_call("Request: DELETE http://example.com/api/delete/123 from unknown")

    @pytest.mark.asyncio
    async def test_Dispatch_WithSlowRequest_ShouldLogLongerProcessTime(self):
        # Arrange
        mockLogger = MagicMock(spec=ILogger)
        mockApp = MagicMock()
        middleware = RequestResponseLoggingMiddleware(app=mockApp, logger=mockLogger)

        mockRequest = MagicMock(spec=Request)
        mockRequest.method = "GET"
        mockRequest.url = MagicMock()
        mockRequest.url.__str__ = MagicMock(return_value="http://example.com/api/slow")
        mockRequest.headers = Headers({})
        mockRequest.client = MagicMock()
        mockRequest.client.host = "127.0.0.1"
        mockRequest.query_params = QueryParams()

        mockResponse = MagicMock(spec=Response)
        mockResponse.status_code = 200
        mockResponse.headers = {}

        mockCallNext = AsyncMock(return_value=mockResponse)

        # Act - simulate 2.5 second process time
        with patch("time.time", side_effect=[5000.0, 5002.5]):
            result = await middleware.dispatch(mockRequest, mockCallNext)

        # Assert
        assert mockResponse.headers["X-Process-Time"] == "2.5"
        mockLogger.Info.assert_any_call("Response: 200 for GET http://example.com/api/slow - 2.500s")


class TestErrorMiddleware:
    """Tests for ErrorMiddleware."""

    @pytest.mark.asyncio
    async def test_Dispatch_WithSuccessfulRequest_ShouldReturnResponse(self):
        # Arrange
        mockLogger = MagicMock(spec=ILogger)
        mockApp = MagicMock()
        middleware = ErrorMiddleware(app=mockApp, logger=mockLogger)

        mockRequest = MagicMock(spec=Request)
        mockResponse = MagicMock(spec=Response)

        mockCallNext = AsyncMock(return_value=mockResponse)

        # Act
        result = await middleware.dispatch(mockRequest, mockCallNext)

        # Assert
        assert result == mockResponse
        mockLogger.Error.assert_not_called()

    @pytest.mark.asyncio
    async def test_Dispatch_WithDomainException_ShouldLogAndReturn400(self):
        # Arrange
        mockLogger = MagicMock(spec=ILogger)
        mockApp = MagicMock()
        middleware = ErrorMiddleware(app=mockApp, logger=mockLogger)

        mockRequest = MagicMock(spec=Request)

        # Create a DomainException
        domainException = DomainException("Invalid operation", code=400)

        # Mock call_next to raise DomainException
        mockCallNext = AsyncMock(side_effect=domainException)

        # Act
        result = await middleware.dispatch(mockRequest, mockCallNext)

        # Assert
        assert isinstance(result, Response)
        assert result.status_code == 400
        assert result.body == b"Invalid operation"

        # Verify error was logged
        mockLogger.Error.assert_called_once()
        errorCallArgs = mockLogger.Error.call_args
        assert "Domain exception: Invalid operation" in errorCallArgs[0][0]
        assert errorCallArgs[1]["exc_info"] is True

    @pytest.mark.asyncio
    async def test_Dispatch_WithGenericException_ShouldLogAndReturn500(self):
        # Arrange
        mockLogger = MagicMock(spec=ILogger)
        mockApp = MagicMock()
        middleware = ErrorMiddleware(app=mockApp, logger=mockLogger)

        mockRequest = MagicMock(spec=Request)

        # Create a generic exception
        genericException = ValueError("Something went wrong")

        # Mock call_next to raise generic exception
        mockCallNext = AsyncMock(side_effect=genericException)

        # Act
        result = await middleware.dispatch(mockRequest, mockCallNext)

        # Assert
        assert isinstance(result, Response)
        assert result.status_code == 500
        assert result.body == b"Internal server error"

        # Verify error was logged
        mockLogger.Error.assert_called_once()
        errorCallArgs = mockLogger.Error.call_args
        assert "Unhandled exception: Something went wrong" in errorCallArgs[0][0]
        assert errorCallArgs[1]["exc_info"] is True

    @pytest.mark.asyncio
    async def test_Dispatch_WithRuntimeError_ShouldReturn500(self):
        # Arrange
        mockLogger = MagicMock(spec=ILogger)
        mockApp = MagicMock()
        middleware = ErrorMiddleware(app=mockApp, logger=mockLogger)

        mockRequest = MagicMock(spec=Request)

        # Mock call_next to raise RuntimeError
        mockCallNext = AsyncMock(side_effect=RuntimeError("Critical failure"))

        # Act
        result = await middleware.dispatch(mockRequest, mockCallNext)

        # Assert
        assert isinstance(result, Response)
        assert result.status_code == 500
        assert result.body == b"Internal server error"

        # Verify error was logged with correct message
        errorCallArgs = mockLogger.Error.call_args
        assert "Unhandled exception: Critical failure" in errorCallArgs[0][0]

    @pytest.mark.asyncio
    async def test_Dispatch_WithDomainExceptionCustomMessage_ShouldReturnMessage(self):
        # Arrange
        mockLogger = MagicMock(spec=ILogger)
        mockApp = MagicMock()
        middleware = ErrorMiddleware(app=mockApp, logger=mockLogger)

        mockRequest = MagicMock(spec=Request)

        # Create DomainException with custom message
        domainException = DomainException("User not found", code=404)

        # Mock call_next to raise DomainException
        mockCallNext = AsyncMock(side_effect=domainException)

        # Act
        result = await middleware.dispatch(mockRequest, mockCallNext)

        # Assert
        assert isinstance(result, Response)
        assert result.status_code == 400  # ErrorMiddleware always returns 400 for DomainException
        assert result.body == b"User not found"
