"""
Unit tests for Events Domain Exceptions.

Tests all custom exception classes in the Events domain.
"""

import pytest

from MiravejaCore.Shared.Events.Domain.Exceptions import (
    MissingEventTypeError,
    MissingEventVersionError,
    SchemaValidationError,
    EventAlreadyRegisteredError,
    EventNotFoundError,
    SchemasDirectoryNotFoundError,
    SchemaFileNotFoundError,
    InvalidSchemaJSONError,
    InvalidJsonStringError,
    EventValidationError,
)
from MiravejaCore.Shared.Errors.Models import DomainException


class TestMissingEventTypeError:
    """Tests for MissingEventTypeError."""

    def test_Initialize_ShouldSetCorrectMessage(self):
        # Act
        exception = MissingEventTypeError()

        # Assert
        assert str(exception) == "Event data missing 'type' field."
        assert isinstance(exception, DomainException)

    def test_Raise_ShouldBeRaisable(self):
        # Act & Assert
        with pytest.raises(MissingEventTypeError) as excInfo:
            raise MissingEventTypeError()

        assert "Event data missing 'type' field." in str(excInfo.value)


class TestMissingEventVersionError:
    """Tests for MissingEventVersionError."""

    def test_Initialize_ShouldSetCorrectMessage(self):
        # Act
        exception = MissingEventVersionError()

        # Assert
        assert str(exception) == "Event data missing 'version' field."
        assert isinstance(exception, DomainException)

    def test_Raise_ShouldBeRaisable(self):
        # Act & Assert
        with pytest.raises(MissingEventVersionError) as excInfo:
            raise MissingEventVersionError()

        assert "Event data missing 'version' field." in str(excInfo.value)


class TestSchemaValidationError:
    """Tests for SchemaValidationError."""

    def test_Initialize_WithMessage_ShouldFormatMessage(self):
        # Act
        exception = SchemaValidationError("Field 'name' is required")

        # Assert
        assert str(exception) == "Schema validation error: Field 'name' is required"
        assert isinstance(exception, DomainException)

    def test_Initialize_WithDifferentMessage_ShouldFormatCorrectly(self):
        # Act
        exception = SchemaValidationError("Invalid type for field 'age'")

        # Assert
        assert "Schema validation error: Invalid type for field 'age'" in str(exception)


class TestEventAlreadyRegisteredError:
    """Tests for EventAlreadyRegisteredError."""

    def test_Initialize_WithTypeAndVersion_ShouldFormatMessage(self):
        # Act
        exception = EventAlreadyRegisteredError("member.created", 1)

        # Assert
        expectedMessage = "Event type 'member.created' with version '1' is already registered."
        assert str(exception) == expectedMessage
        assert isinstance(exception, DomainException)

    def test_Initialize_WithDifferentValues_ShouldFormatCorrectly(self):
        # Act
        exception = EventAlreadyRegisteredError("image.uploaded", 2)

        # Assert
        assert "Event type 'image.uploaded'" in str(exception)
        assert "version '2'" in str(exception)


class TestEventNotFoundError:
    """Tests for EventNotFoundError."""

    def test_Initialize_WithTypeAndVersion_ShouldFormatMessage(self):
        # Act
        exception = EventNotFoundError("member.deleted", 1)

        # Assert
        expectedMessage = "Event type 'member.deleted' with version '1' not found in the registry."
        assert str(exception) == expectedMessage
        assert isinstance(exception, DomainException)

    def test_Initialize_WithHigherVersion_ShouldFormatCorrectly(self):
        # Act
        exception = EventNotFoundError("order.processed", 5)

        # Assert
        assert "Event type 'order.processed'" in str(exception)
        assert "version '5'" in str(exception)
        assert "not found in the registry" in str(exception)


class TestSchemasDirectoryNotFoundError:
    """Tests for SchemasDirectoryNotFoundError."""

    def test_Initialize_WithPath_ShouldFormatMessage(self):
        # Act
        exception = SchemasDirectoryNotFoundError("/path/to/schemas")

        # Assert
        expectedMessage = "Schemas directory not found at path: /path/to/schemas"
        assert str(exception) == expectedMessage
        assert isinstance(exception, DomainException)

    def test_Initialize_WithWindowsPath_ShouldFormatCorrectly(self):
        # Act
        exception = SchemasDirectoryNotFoundError("C:\\schemas\\events")

        # Assert
        assert "Schemas directory not found at path: C:\\schemas\\events" in str(exception)


class TestSchemaFileNotFoundError:
    """Tests for SchemaFileNotFoundError."""

    def test_Initialize_WithFilePath_ShouldFormatMessage(self):
        # Act
        exception = SchemaFileNotFoundError("/schemas/member.created.v1.json")

        # Assert
        expectedMessage = "Schema file not found at path: /schemas/member.created.v1.json"
        assert str(exception) == expectedMessage
        assert isinstance(exception, DomainException)

    def test_Initialize_WithRelativePath_ShouldFormatCorrectly(self):
        # Act
        exception = SchemaFileNotFoundError("./events/image.uploaded.v2.json")

        # Assert
        assert "Schema file not found at path: ./events/image.uploaded.v2.json" in str(exception)


class TestInvalidSchemaJSONError:
    """Tests for InvalidSchemaJSONError."""

    def test_Initialize_WithFilePathAndError_ShouldFormatMessage(self):
        # Act
        exception = InvalidSchemaJSONError("/schemas/event.json", "Unexpected token at line 5")

        # Assert
        expectedMessage = "Invalid JSON in schema file at path: /schemas/event.json. Error: Unexpected token at line 5"
        assert str(exception) == expectedMessage
        assert isinstance(exception, DomainException)

    def test_Initialize_WithDifferentError_ShouldFormatCorrectly(self):
        # Act
        exception = InvalidSchemaJSONError("schema.json", "Missing closing bracket")

        # Assert
        assert "Invalid JSON in schema file at path: schema.json" in str(exception)
        assert "Error: Missing closing bracket" in str(exception)


class TestInvalidJsonStringError:
    """Tests for InvalidJsonStringError."""

    def test_Initialize_WithMessage_ShouldFormatMessage(self):
        # Act
        exception = InvalidJsonStringError("Unexpected end of JSON input")

        # Assert
        expectedMessage = "Invalid JSON string: Unexpected end of JSON input"
        assert str(exception) == expectedMessage
        assert isinstance(exception, DomainException)

    def test_Initialize_WithDifferentMessage_ShouldFormatCorrectly(self):
        # Act
        exception = InvalidJsonStringError("Cannot parse malformed JSON")

        # Assert
        assert "Invalid JSON string: Cannot parse malformed JSON" in str(exception)


class TestEventValidationError:
    """Tests for EventValidationError."""

    def test_Initialize_WithMessage_ShouldFormatMessage(self):
        # Act
        exception = EventValidationError("Required field 'aggregateId' is missing")

        # Assert
        expectedMessage = "Event validation error: Required field 'aggregateId' is missing"
        assert str(exception) == expectedMessage
        assert isinstance(exception, DomainException)

    def test_Initialize_WithValidationDetails_ShouldFormatCorrectly(self):
        # Act
        exception = EventValidationError("Field 'timestamp' must be in ISO format")

        # Assert
        assert "Event validation error: Field 'timestamp' must be in ISO format" in str(exception)

    def test_Raise_ShouldBeRaisable(self):
        # Act & Assert
        with pytest.raises(EventValidationError) as excInfo:
            raise EventValidationError("Validation failed")

        assert "Event validation error: Validation failed" in str(excInfo.value)
