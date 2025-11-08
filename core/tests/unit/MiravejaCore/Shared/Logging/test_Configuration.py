import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError

from MiravejaCore.Shared.Logging.Configuration import LoggerConfig
from MiravejaCore.Shared.Logging.Enums import LoggerLevel, LoggerTarget


class TestLoggerConfig:
    """Test cases for LoggerConfig model."""

    def test_InitializeWithDefaults_ShouldSetDefaultValues(self):
        """Test that LoggerConfig initializes with default values."""
        # Act
        config = LoggerConfig()

        # Assert
        assert config.name == "miraveja"
        assert config.level == LoggerLevel.INFO
        assert config.target == LoggerTarget.CONSOLE
        assert config.format is None
        assert config.datefmt is None
        assert config.filename is None

    def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
        """Test that LoggerConfig initializes with custom values."""
        # Act
        config = LoggerConfig(
            name="custom-logger",
            level=LoggerLevel.DEBUG,
            target=LoggerTarget.CONSOLE,
            format="%(levelname)s: %(message)s",
            datefmt="%Y-%m-%d",
        )

        # Assert
        assert config.name == "custom-logger"
        assert config.level == LoggerLevel.DEBUG
        assert config.target == LoggerTarget.CONSOLE
        assert config.format == "%(levelname)s: %(message)s"
        assert config.datefmt == "%Y-%m-%d"

    @patch.dict(
        os.environ, {"LOGGER_NAME": "test-logger", "LOGGER_LEVEL": "DEBUG", "LOGGER_TARGET": "CONSOLE"}, clear=True
    )
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
        """Test that FromEnv creates config from environment variables."""
        # Act
        config = LoggerConfig.FromEnv()

        # Assert
        assert config.name == "test-logger"
        assert config.level == LoggerLevel.DEBUG
        assert config.target == LoggerTarget.CONSOLE

    @patch.dict(os.environ, {}, clear=True)
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(self):
        """Test that FromEnv uses default values when no environment variables are set."""
        # Act
        config = LoggerConfig.FromEnv()

        # Assert
        assert config.name == "miraveja"
        assert config.level == LoggerLevel.INFO
        assert config.target == LoggerTarget.CONSOLE
        assert config.filename is None

    @patch.dict(
        os.environ, {"LOGGER_TARGET": "FILE", "LOGGER_FILENAME": "app.log", "LOGGER_DIR": "/var/log"}, clear=True
    )
    def test_FromEnvWithFilenameSet_ShouldBuildCorrectFilename(self):
        """Test that FromEnv builds filename from LOGGER_DIR and LOGGER_FILENAME."""
        # Act
        config = LoggerConfig.FromEnv()

        # Assert
        assert config.filename == "/var/log/app.log"
        assert config.target == LoggerTarget.FILE

    @patch.dict(os.environ, {"LOGGER_TARGET": "FILE"}, clear=True)
    def test_FromEnvWithFileTargetAndNoFilename_ShouldProvideDefaultFilename(self):
        """Test that FromEnv provides default filename when target is FILE but no filename is set."""
        # Act
        config = LoggerConfig.FromEnv(defaultName="TestApp")

        # Assert
        assert config.filename == "./logs/testapp.log"
        assert config.target == LoggerTarget.FILE

    @patch.dict(os.environ, {"LOGGER_TARGET": "JSON", "LOGGER_DIR": "/custom/logs"}, clear=True)
    def test_FromEnvWithJsonTargetAndCustomDir_ShouldUseCustomDirectory(self):
        """Test that FromEnv uses custom directory for JSON target."""
        # Act
        config = LoggerConfig.FromEnv(defaultName="MyService")

        # Assert
        assert config.filename == "/custom/logs/myservice.log"
        assert config.target == LoggerTarget.JSON

    @patch.dict(os.environ, {"LOGGER_TARGET": "FILE", "LOGGER_FILENAME": "custom.log"}, clear=True)
    def test_FromEnvWithFilenameButNoDir_ShouldUseCurrentDirectory(self):
        """Test that FromEnv uses current directory when LOGGER_DIR is not set."""
        # Act
        config = LoggerConfig.FromEnv()

        # Assert
        assert config.filename == "./custom.log"

    @patch.dict(os.environ, {"LOGGER_TARGET": "CONSOLE"}, clear=True)
    def test_FromEnvWithConsoleTarget_ShouldNotSetFilename(self):
        """Test that FromEnv does not set filename for CONSOLE target."""
        # Act
        config = LoggerConfig.FromEnv()

        # Assert
        assert config.filename is None
        assert config.target == LoggerTarget.CONSOLE

    @patch.dict(os.environ, {"LOGGER_NAME": "custom"}, clear=True)
    def test_FromEnvWithCustomDefaultTarget_ShouldUseProvidedDefault(self):
        """Test that FromEnv uses provided default target."""
        # Act
        config = LoggerConfig.FromEnv(defaultTarget=LoggerTarget.FILE)

        # Assert
        assert config.target == LoggerTarget.FILE
        # Should provide default filename for FILE target
        assert config.filename is not None

    def test_ValidateFilenameWithFileTargetAndNoFilename_ShouldRaiseValidationError(self):
        """Test that validation raises error when target is FILE but no filename is set."""
        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            LoggerConfig(name="test", target=LoggerTarget.FILE, filename=None)

        assert "Filename must be set when target is FILE or JSON" in str(excInfo.value)

    def test_ValidateFilenameWithJsonTargetAndNoFilename_ShouldRaiseValidationError(self):
        """Test that validation raises error when target is JSON but no filename is set."""
        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            LoggerConfig(name="test", target=LoggerTarget.JSON, filename=None)

        assert "Filename must be set when target is FILE or JSON" in str(excInfo.value)

    @patch("os.makedirs")
    def test_ValidateFilenameWithDirectoryPath_ShouldCreateDirectory(self, mockMakedirs):
        """Test that filename validation creates necessary directories."""
        # Act
        config = LoggerConfig(name="test", target=LoggerTarget.FILE, filename="/path/to/logs/app.log")

        # Assert
        mockMakedirs.assert_called_once_with("/path/to/logs", exist_ok=True)
        assert config.filename == "/path/to/logs/app.log"

    def test_ValidateFilenameWithConsoleTarget_ShouldAllowNoneFilename(self):
        """Test that validation allows None filename for CONSOLE target."""
        # Act
        config = LoggerConfig(name="test", target=LoggerTarget.CONSOLE, filename=None)

        # Assert
        assert config.filename is None
        assert config.target == LoggerTarget.CONSOLE
