import pytest  # type: ignore
from unittest.mock import patch, MagicMock
from logging import Logger as PythonLogger
import logging

from MiravejaCore.Shared.Logging.Models import Logger


class TestLogger:
    """Test cases for Logger model that implements ILogger interface."""

    def test_InitializeWithDefaultName_ShouldCreateLoggerWithDefaultName(self):
        """Test that Logger initializes with default name 'miraveja'."""
        logger = Logger()

        # Access protected member for testing purposes
        assert hasattr(logger, "_logger")
        assert logger._logger.name == "miraveja"  # type: ignore
        assert isinstance(logger._logger, PythonLogger)  # type: ignore

    def test_InitializeWithCustomName_ShouldCreateLoggerWithCustomName(self):
        """Test that Logger initializes with custom name."""
        custom_name = "custom-logger"
        logger = Logger(custom_name)

        assert logger._logger.name == custom_name  # type: ignore

    @patch("logging.getLogger")
    def test_InitializeWithExistingHandlers_ShouldNotAddDuplicateHandlers(self, mock_get_logger: MagicMock):
        """Test that Logger doesn't add handlers if they already exist."""
        mock_python_logger = MagicMock()
        mock_python_logger.handlers = [MagicMock()]  # Already has handlers
        mock_get_logger.return_value = mock_python_logger

        Logger("test")

        # Should not call addHandler since handlers already exist
        mock_python_logger.addHandler.assert_not_called()

    @patch("logging.getLogger")
    def test_InitializeWithNoHandlers_ShouldAddStreamHandler(self, mock_get_logger: MagicMock):
        """Test that Logger adds StreamHandler when no handlers exist."""
        mock_python_logger = MagicMock()
        mock_python_logger.handlers = []  # No handlers
        mock_get_logger.return_value = mock_python_logger

        with patch("logging.StreamHandler") as mock_stream_handler:
            with patch("logging.Formatter") as mock_formatter:
                Logger("test")

                mock_stream_handler.assert_called_once()
                mock_formatter.assert_called_once_with("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
                mock_python_logger.addHandler.assert_called_once()
                mock_python_logger.setLevel.assert_called_once_with(logging.INFO)

    def test_DebugWithMessage_ShouldCallLoggerDebug(self):
        """Test that Debug method calls underlying logger's debug method."""
        logger = Logger("test")

        with patch.object(logger._logger, "debug") as mock_debug:  # type: ignore
            logger.Debug("Test debug message")

            mock_debug.assert_called_once_with("Test debug message")

    def test_DebugWithMessageAndArgs_ShouldCallLoggerDebugWithArgs(self):
        """Test that Debug method passes args to underlying logger."""
        logger = Logger("test")

        with patch.object(logger._logger, "debug") as mock_debug:  # type: ignore
            logger.Debug("Test %s message", "debug")  # type: ignore

            mock_debug.assert_called_once_with("Test %s message", "debug")

    def test_DebugWithMessageAndKwargs_ShouldCallLoggerDebugWithKwargs(self):
        """Test that Debug method passes kwargs to underlying logger."""
        logger = Logger("test")

        with patch.object(logger._logger, "debug") as mock_debug:  # type: ignore
            logger.Debug("Test message", exc_info=True)  # type: ignore

            mock_debug.assert_called_once_with("Test message", exc_info=True)

    def test_InfoWithMessage_ShouldCallLoggerInfo(self):
        """Test that Info method calls underlying logger's info method."""
        logger = Logger("test")

        with patch.object(logger._logger, "info") as mock_info:  # type: ignore
            logger.Info("Test info message")

            mock_info.assert_called_once_with("Test info message")

    def test_InfoWithMessageAndArgs_ShouldCallLoggerInfoWithArgs(self):
        """Test that Info method passes args to underlying logger."""
        logger = Logger("test")

        with patch.object(logger._logger, "info") as mock_info:  # type: ignore
            logger.Info("Test %s message", "info")  # type: ignore

            mock_info.assert_called_once_with("Test %s message", "info")

    def test_WarningWithMessage_ShouldCallLoggerWarning(self):
        """Test that Warning method calls underlying logger's warning method."""
        logger = Logger("test")

        with patch.object(logger._logger, "warning") as mock_warning:  # type: ignore
            logger.Warning("Test warning message")

            mock_warning.assert_called_once_with("Test warning message")

    def test_WarningWithMessageAndKwargs_ShouldCallLoggerWarningWithKwargs(self):
        """Test that Warning method passes kwargs to underlying logger."""
        logger = Logger("test")

        with patch.object(logger._logger, "warning") as mock_warning:  # type: ignore
            logger.Warning("Test message", extra={"key": "value"})

            mock_warning.assert_called_once_with("Test message", extra={"key": "value"})

    def test_ErrorWithMessage_ShouldCallLoggerError(self):
        """Test that Error method calls underlying logger's error method."""
        logger = Logger("test")

        with patch.object(logger._logger, "error") as mock_error:  # type: ignore
            logger.Error("Test error message")

            mock_error.assert_called_once_with("Test error message")

    def test_ErrorWithMessageAndExcInfo_ShouldCallLoggerErrorWithExcInfo(self):
        """Test that Error method can pass exc_info for exception logging."""
        logger = Logger("test")

        with patch.object(logger._logger, "error") as mock_error:  # type: ignore
            logger.Error("Test error", exc_info=True)  # type: ignore

            mock_error.assert_called_once_with("Test error", exc_info=True)

    def test_CriticalWithMessage_ShouldCallLoggerCritical(self):
        """Test that Critical method calls underlying logger's critical method."""
        logger = Logger("test")

        with patch.object(logger._logger, "critical") as mock_critical:  # type: ignore
            logger.Critical("Test critical message")

            mock_critical.assert_called_once_with("Test critical message")

    def test_CriticalWithMultipleArgs_ShouldCallLoggerCriticalWithAllArgs(self):
        """Test that Critical method passes multiple args to underlying logger."""
        logger = Logger("test")

        with patch.object(logger._logger, "critical") as mock_critical:  # type: ignore
            logger.Critical("Test %s %s", "critical", "message")  # type: ignore

            mock_critical.assert_called_once_with("Test %s %s", "critical", "message")

    def test_AllLogLevelsWithArgsAndKwargs_ShouldPassBothCorrectly(self):
        """Test that all log methods can handle both args and kwargs simultaneously."""
        logger = Logger("test")

        with (
            patch.object(logger._logger, "debug") as mock_debug,  # type: ignore
            patch.object(logger._logger, "info") as mock_info,  # type: ignore
            patch.object(logger._logger, "warning") as mock_warning,  # type: ignore
            patch.object(logger._logger, "error") as mock_error,  # type: ignore
            patch.object(logger._logger, "critical") as mock_critical,  # type: ignore
        ):

            logger.Debug("Debug %s", "test", exc_info=False)  # type: ignore
            logger.Info("Info %s", "test", extra={"key": "value"})  # type: ignore
            logger.Warning("Warning %s", "test", stack_info=True)  # type: ignore
            logger.Error("Error %s", "test", exc_info=True)  # type: ignore
            logger.Critical("Critical %s", "test", stacklevel=2)  # type: ignore

            mock_debug.assert_called_once_with("Debug %s", "test", exc_info=False)
            mock_info.assert_called_once_with("Info %s", "test", extra={"key": "value"})
            mock_warning.assert_called_once_with("Warning %s", "test", stack_info=True)
            mock_error.assert_called_once_with("Error %s", "test", exc_info=True)
            mock_critical.assert_called_once_with("Critical %s", "test", stacklevel=2)

    def test_EmptyStringMessage_ShouldAcceptEmptyMessages(self):
        """Test that all log methods accept empty string messages."""
        logger = Logger("test")

        with (
            patch.object(logger._logger, "debug") as mock_debug,  # type: ignore
            patch.object(logger._logger, "info") as mock_info,  # type: ignore
            patch.object(logger._logger, "warning") as mock_warning,  # type: ignore
            patch.object(logger._logger, "error") as mock_error,  # type: ignore
            patch.object(logger._logger, "critical") as mock_critical,  # type: ignore
        ):

            logger.Debug("")
            logger.Info("")
            logger.Warning("")
            logger.Error("")
            logger.Critical("")

            mock_debug.assert_called_once_with("")
            mock_info.assert_called_once_with("")
            mock_warning.assert_called_once_with("")
            mock_error.assert_called_once_with("")
            mock_critical.assert_called_once_with("")

    def test_LoggerInheritanceFromILogger_ShouldImplementInterface(self):
        """Test that Logger properly implements ILogger interface."""
        from MiravejaCore.Shared.Logging.Interfaces import ILogger

        logger = Logger("test")

        assert isinstance(logger, ILogger)

        # Verify all interface methods are implemented
        assert hasattr(logger, "Debug")
        assert hasattr(logger, "Info")
        assert hasattr(logger, "Warning")
        assert hasattr(logger, "Error")
        assert hasattr(logger, "Critical")

        # Verify methods are callable
        assert callable(logger.Debug)
        assert callable(logger.Info)
        assert callable(logger.Warning)
        assert callable(logger.Error)
        assert callable(logger.Critical)
