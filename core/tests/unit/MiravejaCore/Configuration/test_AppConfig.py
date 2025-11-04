import os
from unittest.mock import patch

from MiravejaCore.Shared.Configuration import AppConfig
from MiravejaCore.Shared.Logging.Configuration import LoggerConfig
from MiravejaCore.Shared.DatabaseManager.Domain.Configuration import DatabaseConfig
from MiravejaCore.Shared.Keycloak.Domain.Configuration import KeycloakConfig


class TestAppConfig:
    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        config = AppConfig()
        assert config.appName == "Miraveja Application"
        assert config.appVersion == "0.0.0"
        assert isinstance(config.loggerConfig, LoggerConfig)
        assert isinstance(config.databaseConfig, DatabaseConfig)
        assert isinstance(config.keycloakConfig, KeycloakConfig)

    @patch.dict(os.environ, {"APP_NAME": "Test App", "APP_VERSION": "1.0.0"})
    def test_FromEnvWithEnvironmentVariables_ShouldSetCorrectValues(self):
        config = AppConfig.FromEnv()
        assert config.appName == "Test App"
        assert config.appVersion == "1.0.0"
