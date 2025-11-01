import pytest

from MiravejaApi.Shared.Logging.Exceptions import LoggerAlreadyExistsException


class TestLoggerAlreadyExistsException:
    """Test cases for LoggerAlreadyExistsException domain exception."""

    def test_InitializeWithLoggerName_ShouldSetCorrectMessage(self):
        """Test that LoggerAlreadyExistsException initializes with correct error message."""
        # Arrange
        logger_name = "TestLogger"
        expected_message = f"Logger with name '{logger_name}' already exists."
        expected_code = 500

        # Act
        exception = LoggerAlreadyExistsException(logger_name)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code

    def test_InitializeWithEmptyLoggerName_ShouldSetCorrectMessage(self):
        """Test that LoggerAlreadyExistsException initializes correctly with empty logger name."""
        # Arrange
        logger_name = ""
        expected_message = f"Logger with name '{logger_name}' already exists."
        expected_code = 500

        # Act
        exception = LoggerAlreadyExistsException(logger_name)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code

    def test_InitializeWithSpecialCharactersLoggerName_ShouldSetCorrectMessage(self):
        """Test that LoggerAlreadyExistsException handles special characters in logger name."""
        # Arrange
        logger_name = "Logger@#$%^&*()"
        expected_message = f"Logger with name '{logger_name}' already exists."
        expected_code = 500

        # Act
        exception = LoggerAlreadyExistsException(logger_name)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code
