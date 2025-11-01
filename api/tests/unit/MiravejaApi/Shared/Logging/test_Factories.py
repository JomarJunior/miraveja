import pytest
from unittest.mock import patch, MagicMock

from MiravejaApi.Shared.Logging.Factories import LoggerFactory
from MiravejaApi.Shared.Logging.Enums import LoggerLevel, LoggerTarget
from MiravejaApi.Shared.Logging.Exceptions import LoggerAlreadyExistsException
from MiravejaApi.Shared.Logging.Interfaces import ILogger


class TestLoggerFactory:
    """Test cases for LoggerFactory static factory class."""

    @patch("logging.getLogger")
    def test_CreateLoggerWithDefaultValues_ShouldCreateLoggerWithDefaults(self, mock_get_logger):
        """Test that CreateLogger creates logger with default values."""
        # Arrange
        mock_python_logger = MagicMock()
        mock_python_logger.hasHandlers.return_value = False
        mock_get_logger.return_value = mock_python_logger

        # Act
        result = LoggerFactory.CreateLogger()

        # Assert
        assert isinstance(result, ILogger)
        mock_python_logger.hasHandlers.assert_called_once()
        mock_python_logger.addHandler.assert_called_once()
        mock_python_logger.setLevel.assert_called_once_with(LoggerLevel.INFO.value)

    @patch("logging.getLogger")
    def test_CreateLoggerWithCustomName_ShouldCreateLoggerWithCustomName(self, mock_get_logger):
        """Test that CreateLogger creates logger with custom name."""
        # Arrange
        mock_python_logger = MagicMock()
        mock_python_logger.hasHandlers.return_value = False
        mock_get_logger.return_value = mock_python_logger

        custom_name = "CustomLogger"

        # Act
        result = LoggerFactory.CreateLogger(name=custom_name)

        # Assert
        assert isinstance(result, ILogger)
        mock_get_logger.assert_called_with(custom_name)

    @patch("logging.getLogger")
    def test_CreateLoggerWithExistingLogger_ShouldRaiseLoggerAlreadyExistsException(self, mock_get_logger):
        """Test that CreateLogger raises exception when logger already exists."""
        # Arrange
        mock_python_logger = MagicMock()
        mock_python_logger.hasHandlers.return_value = True
        mock_get_logger.return_value = mock_python_logger
        logger_name = "ExistingLogger"

        # Act & Assert
        with pytest.raises(LoggerAlreadyExistsException) as exc_info:
            LoggerFactory.CreateLogger(name=logger_name)

        assert exc_info.value.message == f"Logger with name '{logger_name}' already exists."

    @patch("logging.getLogger")
    def test_CreateLoggerWithDebugLevel_ShouldSetDebugLevel(self, mock_get_logger):
        """Test that CreateLogger sets debug level correctly."""
        # Arrange
        mock_python_logger = MagicMock()
        mock_python_logger.hasHandlers.return_value = False
        mock_get_logger.return_value = mock_python_logger

        # Act
        result = LoggerFactory.CreateLogger(level=LoggerLevel.DEBUG)

        # Assert
        assert isinstance(result, ILogger)
        mock_python_logger.setLevel.assert_called_once_with(LoggerLevel.DEBUG.value)
