import pytest
import os
from unittest.mock import patch, MagicMock

from MiravejaCore.Shared.Configuration import AppConfig
from MiravejaCore.Shared.Logging.Configuration import LoggerConfig
from MiravejaCore.Shared.DatabaseManager.Domain.Configuration import DatabaseConfig
from MiravejaCore.Shared.Events.Domain.Configuration import KafkaConfig
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Shared.Keycloak.Domain.Configuration import KeycloakConfig
from MiravejaCore.Shared.VectorDatabase.Domain.Configuration import QdrantConfig


class TestAppConfig:
    """Test cases for AppConfig model."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that AppConfig initializes with correct default values."""
        # Act
        config = AppConfig()

        # Assert
        assert config.appName == "Miraveja Application"
        assert config.appVersion == "0.0.0"
        assert isinstance(config.loggerConfig, LoggerConfig)
        assert isinstance(config.databaseConfig, DatabaseConfig)
        assert isinstance(config.keycloakConfig, KeycloakConfig)
        assert isinstance(config.kafkaConfig, KafkaConfig)
        assert isinstance(config.minioConfig, MinIoConfig)
        assert isinstance(config.qdrantConfig, QdrantConfig)

    def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
        """Test that AppConfig initializes with custom values correctly."""
        # Arrange
        customAppName = "Custom App"
        customAppVersion = "1.2.3"

        # Act
        config = AppConfig(
            appName=customAppName,
            appVersion=customAppVersion,
        )

        # Assert
        assert config.appName == customAppName
        assert config.appVersion == customAppVersion
        assert isinstance(config.loggerConfig, LoggerConfig)
        assert isinstance(config.databaseConfig, DatabaseConfig)
        assert isinstance(config.keycloakConfig, KeycloakConfig)
        assert isinstance(config.kafkaConfig, KafkaConfig)
        assert isinstance(config.minioConfig, MinIoConfig)
        assert isinstance(config.qdrantConfig, QdrantConfig)

    @patch.dict(
        os.environ,
        {
            "APP_NAME": "Test Application",
            "APP_VERSION": "2.5.1",
        },
        clear=False,  # Keep existing env vars for nested configs
    )
    @patch("MiravejaCore.Shared.Logging.Configuration.LoggerConfig.FromEnv")
    @patch("MiravejaCore.Shared.DatabaseManager.Domain.Configuration.DatabaseConfig.FromEnv")
    @patch("MiravejaCore.Shared.Keycloak.Domain.Configuration.KeycloakConfig.FromEnv")
    @patch("MiravejaCore.Shared.Events.Domain.Configuration.KafkaConfig.FromEnv")
    @patch("MiravejaCore.Shared.Storage.Domain.Configuration.MinIoConfig.FromEnv")
    @patch("MiravejaCore.Shared.VectorDatabase.Domain.Configuration.QdrantConfig.FromEnv")
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(
        self,
        mockQdrantFromEnv,
        mockMinioFromEnv,
        mockKafkaFromEnv,
        mockKeycloakFromEnv,
        mockDatabaseFromEnv,
        mockLoggerFromEnv,
    ):
        """Test that AppConfig.FromEnv creates instance from environment variables."""
        # Arrange - Create mock configs using MagicMock to avoid validation issues
        mockLoggerConfig = MagicMock(spec=LoggerConfig)
        mockDatabaseConfig = MagicMock(spec=DatabaseConfig)
        mockKeycloakConfig = MagicMock(spec=KeycloakConfig)
        mockKafkaConfig = MagicMock(spec=KafkaConfig)
        mockMinioConfig = MagicMock(spec=MinIoConfig)
        mockQdrantConfig = MagicMock(spec=QdrantConfig)

        mockLoggerFromEnv.return_value = mockLoggerConfig
        mockDatabaseFromEnv.return_value = mockDatabaseConfig
        mockKeycloakFromEnv.return_value = mockKeycloakConfig
        mockKafkaFromEnv.return_value = mockKafkaConfig
        mockMinioFromEnv.return_value = mockMinioConfig
        mockQdrantFromEnv.return_value = mockQdrantConfig

        # Act
        config = AppConfig.FromEnv()

        # Assert
        assert config.appName == "Test Application"
        assert config.appVersion == "2.5.1"
        assert config.loggerConfig == mockLoggerConfig
        assert config.databaseConfig == mockDatabaseConfig
        assert config.keycloakConfig == mockKeycloakConfig
        assert config.kafkaConfig == mockKafkaConfig
        assert config.minioConfig == mockMinioConfig
        assert config.qdrantConfig == mockQdrantConfig

        # Verify all FromEnv methods were called
        mockLoggerFromEnv.assert_called_once()
        mockDatabaseFromEnv.assert_called_once()
        mockKeycloakFromEnv.assert_called_once()
        mockKafkaFromEnv.assert_called_once()
        mockMinioFromEnv.assert_called_once()
        mockQdrantFromEnv.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    @patch("MiravejaCore.Shared.Logging.Configuration.LoggerConfig.FromEnv")
    @patch("MiravejaCore.Shared.DatabaseManager.Domain.Configuration.DatabaseConfig.FromEnv")
    @patch("MiravejaCore.Shared.Keycloak.Domain.Configuration.KeycloakConfig.FromEnv")
    @patch("MiravejaCore.Shared.Events.Domain.Configuration.KafkaConfig.FromEnv")
    @patch("MiravejaCore.Shared.Storage.Domain.Configuration.MinIoConfig.FromEnv")
    @patch("MiravejaCore.Shared.VectorDatabase.Domain.Configuration.QdrantConfig.FromEnv")
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(
        self,
        mockQdrantFromEnv,
        mockMinioFromEnv,
        mockKafkaFromEnv,
        mockKeycloakFromEnv,
        mockDatabaseFromEnv,
        mockLoggerFromEnv,
    ):
        """Test that AppConfig.FromEnv uses default values when environment variables are missing."""
        # Arrange - Create mock configs
        mockLoggerConfig = MagicMock(spec=LoggerConfig)
        mockDatabaseConfig = MagicMock(spec=DatabaseConfig)
        mockKeycloakConfig = MagicMock(spec=KeycloakConfig)
        mockKafkaConfig = MagicMock(spec=KafkaConfig)
        mockMinioConfig = MagicMock(spec=MinIoConfig)
        mockQdrantConfig = MagicMock(spec=QdrantConfig)

        mockLoggerFromEnv.return_value = mockLoggerConfig
        mockDatabaseFromEnv.return_value = mockDatabaseConfig
        mockKeycloakFromEnv.return_value = mockKeycloakConfig
        mockKafkaFromEnv.return_value = mockKafkaConfig
        mockMinioFromEnv.return_value = mockMinioConfig
        mockQdrantFromEnv.return_value = mockQdrantConfig

        # Act
        config = AppConfig.FromEnv()

        # Assert - Should use built-in defaults
        assert config.appName == "Miraveja Application"
        assert config.appVersion == "0.0.0"
        assert config.loggerConfig == mockLoggerConfig
        assert config.databaseConfig == mockDatabaseConfig
        assert config.keycloakConfig == mockKeycloakConfig
        assert config.kafkaConfig == mockKafkaConfig
        assert config.minioConfig == mockMinioConfig
        assert config.qdrantConfig == mockQdrantConfig
