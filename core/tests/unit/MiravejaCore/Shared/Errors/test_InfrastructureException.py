import pytest
from typing import Dict, Any

from MiravejaCore.Shared.Errors.Models import InfrastructureException


class TestInfrastructureException:
    """Test cases for InfrastructureException error model."""

    def test_InitializeWithMessageOnly_ShouldSetCorrectDefaults(self):
        """Test that InfrastructureException initializes with message and default values."""
        message = "Test infrastructure error"
        exception = InfrastructureException(message)

        assert exception.message == message
        assert exception.code == 500
        assert exception.details is None
        assert str(exception) == message

    def test_InitializeWithMessageAndCode_ShouldSetCorrectValues(self):
        """Test that InfrastructureException initializes with custom message and code."""
        message = "Custom infrastructure error"
        code = 503
        exception = InfrastructureException(message, code)

        assert exception.message == message
        assert exception.code == code
        assert exception.details is None
        assert str(exception) == message

    def test_InitializeWithAllParameters_ShouldSetCorrectValues(self):
        """Test that InfrastructureException initializes with all custom parameters."""
        message = "Detailed infrastructure error"
        code = 502
        details = {"service": "database", "error_type": "connection_timeout"}
        exception = InfrastructureException(message, code, details)

        assert exception.message == message
        assert exception.code == code
        assert exception.details == details
        assert str(exception) == message

    def test_InitializeWithEmptyMessage_ShouldAllowEmptyString(self):
        """Test that InfrastructureException allows empty message string."""
        exception = InfrastructureException("")

        assert exception.message == ""
        assert exception.code == 500
        assert exception.details is None

    def test_InitializeWithNoneDetails_ShouldSetDetailsToNone(self):
        """Test that InfrastructureException allows None for details."""
        exception = InfrastructureException("Test message", 500, None)

        assert exception.details is None

    def test_InitializeWithEmptyDetailsDict_ShouldSetEmptyDict(self):
        """Test that InfrastructureException allows empty dictionary for details."""
        details: Dict[str, str] = {}
        exception = InfrastructureException("Test message", 500, details)

        assert exception.details == details
        assert exception.details is not None
        assert len(exception.details) == 0

    def test_InitializeWithComplexDetails_ShouldPreserveComplexStructure(self):
        """Test that InfrastructureException preserves complex details structure."""
        details: Dict[str, Any] = {
            "errors": [
                {"service": "database", "message": "Connection failed"},
                {"service": "cache", "message": "Timeout"},
            ],
            "request_id": "67890",
            "timestamp": "2023-01-01T00:00:00Z",
            "infrastructure": {"cluster": {"node": "server-01"}},
        }
        exception = InfrastructureException("Infrastructure failure", 503, details)

        assert exception.details == details
        assert exception.details is not None
        assert exception.details["errors"][0]["service"] == "database"
        assert exception.details["infrastructure"]["cluster"]["node"] == "server-01"

    def test_InitializeWithZeroCode_ShouldAllowZeroCode(self):
        """Test that InfrastructureException allows zero for code."""
        exception = InfrastructureException("Test message", 0)

        assert exception.code == 0

    def test_InitializeWithNegativeCode_ShouldAllowNegativeCode(self):
        """Test that InfrastructureException allows negative code values."""
        exception = InfrastructureException("Test message", -1)

        assert exception.code == -1

    def test_InitializeWithLargeCode_ShouldAllowLargeCode(self):
        """Test that InfrastructureException allows large code values."""
        exception = InfrastructureException("Test message", 99999)

        assert exception.code == 99999

    def test_InheritanceFromException_ShouldBeInstanceOfException(self):
        """Test that InfrastructureException inherits from built-in Exception."""
        exception = InfrastructureException("Test message")

        assert isinstance(exception, Exception)
        assert isinstance(exception, InfrastructureException)

    def test_RaiseAndCatchException_ShouldWorkAsStandardException(self):
        """Test that InfrastructureException can be raised and caught like standard exception."""
        message = "Test infrastructure error"
        code = 503
        details = {"service": "redis"}

        with pytest.raises(InfrastructureException) as exc_info:
            raise InfrastructureException(message, code, details)

        caught_exception = exc_info.value
        assert caught_exception.message == message
        assert caught_exception.code == code
        assert caught_exception.details == details

    def test_ReprWithAllParameters_ShouldContainKeyInformation(self):
        """Test that repr contains key exception information."""
        exception = InfrastructureException("Infrastructure error", 502, {"key": "value"})
        repr_str = repr(exception)

        assert "InfrastructureException" in repr_str
        assert "Infrastructure error" in repr_str

    def test_StrMethodShouldReturnMessage(self):
        """Test that str() returns the exception message."""
        message = "Infrastructure error message"
        exception = InfrastructureException(message, 503)

        assert str(exception) == message

    def test_ArgsAttributeShouldContainMessage(self):
        """Test that args attribute contains the exception message."""
        message = "Error message in args"
        exception = InfrastructureException(message)

        assert exception.args == (message,)
        assert exception.args[0] == message

    def test_DefaultCodeDifferentFromDomainException_ShouldBe500(self):
        """Test that InfrastructureException has default code 500 (different from DomainException)."""
        exception = InfrastructureException("Test message")

        assert exception.code == 500  # Infrastructure default is 500, Domain default is 400

    def test_InitializeWithTypicalInfrastructureCodes_ShouldAcceptCommonCodes(self):
        """Test that InfrastructureException accepts typical infrastructure error codes."""
        # Test common infrastructure error codes
        codes = [500, 502, 503, 504, 507, 508, 509, 510, 511]

        for code in codes:
            exception = InfrastructureException("Infrastructure error", code)
            assert exception.code == code

    def test_InitializeWithInfrastructureSpecificDetails_ShouldPreserveStructure(self):
        """Test that InfrastructureException preserves infrastructure-specific details."""
        details: Dict[str, Any] = {
            "database_host": "db-primary.internal",
            "connection_pool_size": 20,
            "retry_count": 3,
            "timeout_ms": 5000,
            "health_check": {"database": False, "cache": True, "message_queue": False},
        }
        exception = InfrastructureException("Service unavailable", 503, details)

        assert exception.details == details
        assert exception.details is not None
        assert exception.details["database_host"] == "db-primary.internal"
        assert exception.details["health_check"]["database"] is False

    def test_InitializeWithNonStringMessage_ShouldAcceptNonString(self):
        """Test that InfrastructureException accepts non-string message types."""
        # Note: This tests the current implementation behavior
        # In a strict implementation, this might be rejected
        message = 12345
        exception = InfrastructureException(message)  # type: ignore

        assert exception.message == message

    def test_InitializeWithNonIntCode_ShouldAcceptNonInt(self):
        """Test that InfrastructureException accepts non-int code types."""
        # Note: This tests the current implementation behavior
        # In a strict implementation, this might be rejected
        code = "500"
        exception = InfrastructureException("Test", code)  # type: ignore

        assert exception.code == code
