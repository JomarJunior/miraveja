import os
from unittest.mock import patch, MagicMock

from MiravejaApi.Configuration.Models import AppConfig, LoggerConfig, DatabaseConfig
from MiravejaApi.Shared.Keycloak.Domain.Models import KeycloakConfig


class TestAppConfig:
    """Test cases for AppConfig model."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that AppConfig initializes with correct default values."""
        config = AppConfig()

        assert config.appName == "Miraveja API"
        assert config.appVersion == "0.0.0"
        assert isinstance(config.loggerConfig, LoggerConfig)
        assert isinstance(config.databaseConfig, DatabaseConfig)
        assert isinstance(config.keycloakConfig, KeycloakConfig)
        assert config.debug is False

    def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
        """Test that AppConfig initializes with custom values correctly."""
        logger_config = LoggerConfig(name="custom-logger")
        database_config = DatabaseConfig(connectionUrl="postgresql://test:test@localhost:5432/test")
        keycloak_config = KeycloakConfig(
            serverUrl="http://custom:8080/auth/",
            realm="custom-realm",
            clientId="custom-client",
            clientSecret="custom-secret",
            verifyServerCertificate=True,
            publicKey=None,
            tokenVerificationAlgorithm="RS256",
            tokenMinimumTimeToLive=30,
        )

        config = AppConfig(
            appName="Custom App",
            appVersion="1.0.0",
            loggerConfig=logger_config,
            databaseConfig=database_config,
            keycloakConfig=keycloak_config,
            debug=True,
        )

        assert config.appName == "Custom App"
        assert config.appVersion == "1.0.0"
        assert config.loggerConfig == logger_config
        assert config.databaseConfig == database_config
        assert config.keycloakConfig == keycloak_config
        assert config.debug is True

    @patch.dict(os.environ, {"APP_NAME": "Test Application", "APP_VERSION": "2.1.0", "DEBUG": "true"})
    @patch("Miraveja.Configuration.Models.LoggerConfig.FromEnv")
    @patch("Miraveja.Configuration.Models.DatabaseConfig.FromEnv")
    @patch("Miraveja.Configuration.Models.KeycloakConfigFactory.FromEnv")
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(
        self, mock_keycloak_from_env: MagicMock, mock_database_from_env: MagicMock, mock_logger_from_env: MagicMock
    ):
        """Test that FromEnv creates AppConfig with all environment variables set."""
        # Setup mocks
        mock_logger_config = LoggerConfig(name="mocked-logger")
        mock_database_config = DatabaseConfig(connectionUrl="postgresql://mock:mock@localhost:5432/mock")
        mock_keycloak_config = KeycloakConfig(
            serverUrl="http://mock:8080/auth/",
            realm="mock-realm",
            clientId="mock-client",
            clientSecret="mock-secret",
            verifyServerCertificate=True,
            publicKey=None,
            tokenVerificationAlgorithm="RS256",
            tokenMinimumTimeToLive=30,
        )

        mock_logger_from_env.return_value = mock_logger_config
        mock_database_from_env.return_value = mock_database_config
        mock_keycloak_from_env.return_value = mock_keycloak_config

        config = AppConfig.FromEnv()

        assert config.appName == "Test Application"
        assert config.appVersion == "2.1.0"
        assert config.debug is True
        assert config.loggerConfig == mock_logger_config
        assert config.databaseConfig == mock_database_config
        assert config.keycloakConfig == mock_keycloak_config

        # Verify that factory methods were called
        mock_logger_from_env.assert_called_once()
        mock_database_from_env.assert_called_once()
        mock_keycloak_from_env.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    @patch("Miraveja.Configuration.Models.LoggerConfig.FromEnv")
    @patch("Miraveja.Configuration.Models.DatabaseConfig.FromEnv")
    @patch("Miraveja.Configuration.Models.KeycloakConfigFactory.FromEnv")
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(
        self, mock_keycloak_from_env: MagicMock, mock_database_from_env: MagicMock, mock_logger_from_env: MagicMock
    ):
        """Test that FromEnv uses default values when no environment variables are set."""
        # Setup mocks
        mock_logger_config = LoggerConfig()
        mock_database_config = DatabaseConfig(connectionUrl="postgresql://user:password@localhost:5432/miraveja")
        mock_keycloak_config = KeycloakConfig(
            serverUrl="http://localhost:8080/auth/",
            realm="miraveja",
            clientId="miraveja-client",
            clientSecret="secret",
            verifyServerCertificate=True,
            publicKey=None,
            tokenVerificationAlgorithm="RS256",
            tokenMinimumTimeToLive=30,
        )

        mock_logger_from_env.return_value = mock_logger_config
        mock_database_from_env.return_value = mock_database_config
        mock_keycloak_from_env.return_value = mock_keycloak_config

        config = AppConfig.FromEnv()

        assert config.appName == "Miraveja API"
        assert config.appVersion == "0.0.0"
        assert config.debug is False

    @patch.dict(os.environ, {"DEBUG": "1"})
    def test_FromEnvWithDebugOne_ShouldSetDebugToTrue(self):
        """Test that FromEnv sets debug to True when DEBUG is '1'."""
        config = AppConfig.FromEnv()

        assert config.debug is True

    @patch.dict(os.environ, {"DEBUG": "yes"})
    def test_FromEnvWithDebugYes_ShouldSetDebugToTrue(self):
        """Test that FromEnv sets debug to True when DEBUG is 'yes'."""
        config = AppConfig.FromEnv()

        assert config.debug is True

    @patch.dict(os.environ, {"DEBUG": "false"})
    def test_FromEnvWithDebugFalse_ShouldSetDebugToFalse(self):
        """Test that FromEnv sets debug to False when DEBUG is 'false'."""
        config = AppConfig.FromEnv()

        assert config.debug is False

    @patch.dict(os.environ, {"DEBUG": "0"})
    def test_FromEnvWithDebugZero_ShouldSetDebugToFalse(self):
        """Test that FromEnv sets debug to False when DEBUG is '0'."""
        config = AppConfig.FromEnv()

        assert config.debug is False

    @patch.dict(os.environ, {"DEBUG": "no"})
    def test_FromEnvWithDebugNo_ShouldSetDebugToFalse(self):
        """Test that FromEnv sets debug to False when DEBUG is 'no'."""
        config = AppConfig.FromEnv()

        assert config.debug is False

    @patch.dict(os.environ, {"DEBUG": "INVALID"})
    def test_FromEnvWithInvalidDebug_ShouldSetDebugToFalse(self):
        """Test that FromEnv sets debug to False when DEBUG is invalid."""
        config = AppConfig.FromEnv()

        assert config.debug is False

    @patch.dict(os.environ, {"APP_NAME": "", "APP_VERSION": ""})
    def test_FromEnvWithEmptyStrings_ShouldAllowEmptyValues(self):
        """Test that FromEnv allows empty strings for string fields."""
        config = AppConfig.FromEnv()

        assert config.appName == ""
        assert config.appVersion == ""

    def test_InitializeWithNoneValues_ShouldUseDefaultFactories(self):
        """Test that AppConfig uses default factories when None values are not allowed."""
        # This test verifies that the default factories are called properly
        config = AppConfig()

        # Verify that default factories created valid configurations
        assert config.loggerConfig.name == "miraveja"
        assert config.databaseConfig.databaseType == "postgresql"
        assert config.keycloakConfig.realm == "miraveja"
