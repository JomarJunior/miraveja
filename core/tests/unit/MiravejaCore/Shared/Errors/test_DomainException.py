import pytest
from typing import Dict, Any

from MiravejaCore.Shared.Errors.Models import DomainException


class TestDomainException:
    """Test cases for DomainException error model."""

    def test_InitializeWithMessageOnly_ShouldSetCorrectDefaults(self):
        """Test that DomainException initializes with message and default values."""
        message = "Test domain error"
        exception = DomainException(message)

        assert exception.message == message
        assert exception.code == 400
        assert exception.details is None
        assert str(exception) == message

    def test_InitializeWithMessageAndCode_ShouldSetCorrectValues(self):
        """Test that DomainException initializes with custom message and code."""
        message = "Custom domain error"
        code = 422
        exception = DomainException(message, code)

        assert exception.message == message
        assert exception.code == code
        assert exception.details is None
        assert str(exception) == message

    def test_InitializeWithAllParameters_ShouldSetCorrectValues(self):
        """Test that DomainException initializes with all custom parameters."""
        message = "Detailed domain error"
        code = 409
        details = {"field": "value", "error_type": "validation"}
        exception = DomainException(message, code, details)

        assert exception.message == message
        assert exception.code == code
        assert exception.details == details
        assert str(exception) == message

    def test_InitializeWithEmptyMessage_ShouldAllowEmptyString(self):
        """Test that DomainException allows empty message string."""
        exception = DomainException("")

        assert exception.message == ""
        assert exception.code == 400
        assert exception.details is None

    def test_InitializeWithNoneDetails_ShouldSetDetailsToNone(self):
        """Test that DomainException allows None for details."""
        exception = DomainException("Test message", 400, None)

        assert exception.details is None

    def test_InitializeWithEmptyDetailsDict_ShouldSetEmptyDict(self):
        """Test that DomainException allows empty dictionary for details."""
        details: Dict[str, str] = {}
        exception = DomainException("Test message", 400, details)

        assert exception.details == details
        assert exception.details is not None
        assert len(exception.details) == 0

    def test_InitializeWithComplexDetails_ShouldPreserveComplexStructure(self):
        """Test that DomainException preserves complex details structure."""
        details: Dict[str, Any] = {
            "errors": [{"field": "email", "message": "Invalid format"}, {"field": "password", "message": "Too short"}],
            "request_id": "12345",
            "timestamp": "2023-01-01T00:00:00Z",
            "nested": {"level1": {"level2": "deep_value"}},
        }
        exception = DomainException("Validation failed", 422, details)

        assert exception.details == details
        assert exception.details is not None
        assert exception.details["errors"][0]["field"] == "email"
        assert exception.details["nested"]["level1"]["level2"] == "deep_value"

    def test_InitializeWithZeroCode_ShouldAllowZeroCode(self):
        """Test that DomainException allows zero for code."""
        exception = DomainException("Test message", 0)

        assert exception.code == 0

    def test_InitializeWithNegativeCode_ShouldAllowNegativeCode(self):
        """Test that DomainException allows negative code values."""
        exception = DomainException("Test message", -1)

        assert exception.code == -1

    def test_InitializeWithLargeCode_ShouldAllowLargeCode(self):
        """Test that DomainException allows large code values."""
        exception = DomainException("Test message", 99999)

        assert exception.code == 99999

    def test_InheritanceFromException_ShouldBeInstanceOfException(self):
        """Test that DomainException inherits from built-in Exception."""
        exception = DomainException("Test message")

        assert isinstance(exception, Exception)
        assert isinstance(exception, DomainException)

    def test_RaiseAndCatchException_ShouldWorkAsStandardException(self):
        """Test that DomainException can be raised and caught like standard exception."""
        message = "Test domain error"
        code = 400
        details = {"test": "data"}

        with pytest.raises(DomainException) as exc_info:
            raise DomainException(message, code, details)

        caught_exception = exc_info.value
        assert caught_exception.message == message
        assert caught_exception.code == code
        assert caught_exception.details == details

    def test_ReprWithAllParameters_ShouldContainKeyInformation(self):
        """Test that repr contains key exception information."""
        exception = DomainException("Test error", 422, {"key": "value"})
        repr_str = repr(exception)

        assert "DomainException" in repr_str
        assert "Test error" in repr_str

    def test_StrMethodShouldReturnMessage(self):
        """Test that str() returns the exception message."""
        message = "Domain error message"
        exception = DomainException(message, 500)

        assert str(exception) == message

    def test_ArgsAttributeShouldContainMessage(self):
        """Test that args attribute contains the exception message."""
        message = "Error message in args"
        exception = DomainException(message)

        assert exception.args == (message,)
        assert exception.args[0] == message

    def test_InitializeWithNonStringMessage_ShouldAcceptNonString(self):
        """Test that DomainException accepts non-string message types."""
        # Note: This tests the current implementation behavior
        # In a strict implementation, this might be rejected
        message = 12345
        exception = DomainException(message)  # type: ignore

        assert exception.message == message

    def test_InitializeWithNonIntCode_ShouldAcceptNonInt(self):
        """Test that DomainException accepts non-int code types."""
        # Note: This tests the current implementation behavior
        # In a strict implementation, this might be rejected
        code = "400"
        exception = DomainException("Test", code)  # type: ignore

        assert exception.code == code
