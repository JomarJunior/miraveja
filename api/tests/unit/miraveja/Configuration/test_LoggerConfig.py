import os
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from Miraveja.Configuration.Models import LoggerConfig
from Miraveja.Shared.Logging.Enums import LoggerLevel, LoggerTarget


class TestLoggerConfig:
    """Test cases for LoggerConfig model."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that LoggerConfig initializes with correct default values."""
        config = LoggerConfig()

        assert config.name == "miraveja"
        assert config.level == LoggerLevel.INFO
        assert config.target == LoggerTarget.CONSOLE
        assert config.format is None
        assert config.datefmt is None
        assert config.filename is None

    def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
        """Test that LoggerConfig initializes with custom values correctly."""
        config = LoggerConfig(
            name="test-logger",
            level=LoggerLevel.DEBUG,
            target=LoggerTarget.FILE,
            format="%(message)s",
            datefmt="%Y-%m-%d",
            filename="/tmp/test.log",
        )

        assert config.name == "test-logger"
        assert config.level == LoggerLevel.DEBUG
        assert config.target == LoggerTarget.FILE
        assert config.format == "%(message)s"
        assert config.datefmt == "%Y-%m-%d"
        assert config.filename == "/tmp/test.log"

    @patch.dict(
        os.environ,
        {
            "LOGGER_NAME": "env-logger",
            "LOGGER_LEVEL": "DEBUG",
            "LOGGER_TARGET": "FILE",
            "LOGGER_FORMAT": "%(levelname)s: %(message)s",
            "LOGGER_DATEFMT": "%H:%M:%S",
            "LOGGER_DIR": "/var/log",
            "LOGGER_FILENAME": "app.log",
        },
    )
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
        """Test that FromEnv creates LoggerConfig with all environment variables set."""
        config = LoggerConfig.FromEnv()

        assert config.name == "env-logger"
        assert config.level == LoggerLevel.DEBUG
        assert config.target == LoggerTarget.FILE
        assert config.format == "%(levelname)s: %(message)s"
        assert config.datefmt == "%H:%M:%S"
        assert config.filename == "/var/log/app.log"

    @patch.dict(os.environ, {}, clear=True)
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(self):
        """Test that FromEnv uses default values when no environment variables are set."""
        config = LoggerConfig.FromEnv()

        assert config.name == "miraveja"
        assert config.level == LoggerLevel.INFO
        assert config.target == LoggerTarget.CONSOLE
        assert config.format is None
        assert config.datefmt is None
        assert config.filename is None

    @patch.dict(os.environ, {"LOGGER_FILENAME": "test.log"})
    def test_FromEnvWithFilenameOnly_ShouldSetRelativeFilename(self):
        """Test that FromEnv sets relative filename when LOGGER_DIR is not set."""
        config = LoggerConfig.FromEnv()

        assert config.filename == "./test.log"

    @patch("os.makedirs")
    def test_ValidateFilenameWithFileTargetAndValidPath_ShouldCreateDirectoryAndReturnPath(
        self, mock_makedirs: MagicMock
    ):
        """Test that filename validation creates directory when target is FILE and filename has directory."""
        config = LoggerConfig(target=LoggerTarget.FILE, filename="/path/to/logs/app.log")

        mock_makedirs.assert_called_once_with("/path/to/logs", exist_ok=True)
        assert config.filename == "/path/to/logs/app.log"

    @patch("os.makedirs")
    def test_ValidateFilenameWithJsonTargetAndValidPath_ShouldCreateDirectoryAndReturnPath(
        self, mock_makedirs: MagicMock
    ):
        """Test that filename validation creates directory when target is JSON and filename has directory."""
        config = LoggerConfig(target=LoggerTarget.JSON, filename="/path/to/logs/app.json")

        mock_makedirs.assert_called_once_with("/path/to/logs", exist_ok=True)
        assert config.filename == "/path/to/logs/app.json"

    def test_ValidateFilenameWithFileTargetAndNoFilename_ShouldRaiseValidationError(self):
        """Test that filename validation raises error when target is FILE but no filename is provided."""
        with pytest.raises(ValidationError) as exc_info:
            LoggerConfig(target=LoggerTarget.FILE, filename=None)

        assert "Filename must be set when target is FILE or JSON" in str(exc_info.value)

    def test_ValidateFilenameWithJsonTargetAndNoFilename_ShouldRaiseValidationError(self):
        """Test that filename validation raises error when target is JSON but no filename is provided."""
        with pytest.raises(ValidationError) as exc_info:
            LoggerConfig(target=LoggerTarget.JSON, filename=None)

        assert "Filename must be set when target is FILE or JSON" in str(exc_info.value)

    def test_ValidateFilenameWithConsoleTargetAndNoFilename_ShouldNotRaiseError(self):
        """Test that filename validation does not raise error when target is CONSOLE and no filename is provided."""
        config = LoggerConfig(target=LoggerTarget.CONSOLE, filename=None)

        assert config.filename is None
        assert config.target == LoggerTarget.CONSOLE

    def test_ValidateFilenameWithFilenameWithoutDirectory_ShouldNotCallMakedirs(self):
        """Test that filename validation does not create directory when filename has no directory path."""
        with patch("os.makedirs") as mock_makedirs:
            config = LoggerConfig(target=LoggerTarget.FILE, filename="app.log")

        mock_makedirs.assert_not_called()
        assert config.filename == "app.log"

    @patch.dict(os.environ, {"LOGGER_LEVEL": "INVALID_LEVEL"})
    def test_FromEnvWithInvalidLoggerLevel_ShouldRaiseValidationError(self):
        """Test that FromEnv raises validation error when LOGGER_LEVEL is invalid."""
        with pytest.raises(ValueError):
            LoggerConfig.FromEnv()

    @patch.dict(os.environ, {"LOGGER_TARGET": "INVALID_TARGET"})
    def test_FromEnvWithInvalidLoggerTarget_ShouldRaiseValidationError(self):
        """Test that FromEnv raises validation error when LOGGER_TARGET is invalid."""
        with pytest.raises(ValueError):
            LoggerConfig.FromEnv()

    def test_InitializeWithInvalidLoggerLevel_ShouldRaiseValidationError(self):
        """Test that initialization raises validation error with invalid logger level."""
        with pytest.raises(ValidationError):
            LoggerConfig(level="INVALID_LEVEL")  # type: ignore

    def test_InitializeWithInvalidLoggerTarget_ShouldRaiseValidationError(self):
        """Test that initialization raises validation error with invalid logger target."""
        with pytest.raises(ValidationError):
            LoggerConfig(target="INVALID_TARGET")  # type: ignore
