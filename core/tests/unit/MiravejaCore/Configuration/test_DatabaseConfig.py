import os
import pytest
from unittest.mock import patch
from pydantic import ValidationError

from MiravejaCore.Shared.DatabaseManager.Domain.Configuration import DatabaseConfig


class TestDatabaseConfig:
    """Test cases for DatabaseConfig model."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that DatabaseConfig initializes with correct default values."""
        config = DatabaseConfig(connectionUrl="postgresql://user:password@localhost:5432/miraveja")

        assert config.databaseType == "postgresql"
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.user == "user"
        assert config.password == "password"
        assert config.database == "miraveja"
        assert config.maxConnections == 10
        assert config.connectionUrl == "postgresql://user:password@localhost:5432/miraveja"

    def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
        """Test that DatabaseConfig initializes with custom values correctly."""
        config = DatabaseConfig(
            databaseType="mysql",
            host="remote-host",
            port=3306,
            user="admin",
            password="secret",
            database="testdb",
            connectionUrl="mysql://admin:secret@remote-host:3306/testdb",
            maxConnections=20,
        )

        assert config.databaseType == "mysql"
        assert config.host == "remote-host"
        assert config.port == 3306
        assert config.user == "admin"
        assert config.password == "secret"
        assert config.database == "testdb"
        assert config.connectionUrl == "mysql://admin:secret@remote-host:3306/testdb"
        assert config.maxConnections == 20

    @patch.dict(
        os.environ,
        {
            "DATABASE_TYPE": "mysql",
            "DATABASE_HOST": "db-server",
            "DATABASE_PORT": "3306",
            "DATABASE_USER": "dbuser",
            "DATABASE_PASSWORD": "dbpass",
            "DATABASE_NAME": "appdb",
            "DATABASE_CONNECTION_URL": "mysql://dbuser:dbpass@db-server:3306/appdb",
            "DATABASE_MAX_CONNECTIONS": "25",
        },
    )
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
        """Test that FromEnv creates DatabaseConfig with all environment variables set."""
        config = DatabaseConfig.FromEnv()

        assert config.databaseType == "mysql"
        assert config.host == "db-server"
        assert config.port == 3306
        assert config.user == "dbuser"
        assert config.password == "dbpass"
        assert config.database == "appdb"
        assert config.connectionUrl == "mysql://dbuser:dbpass@db-server:3306/appdb"
        assert config.maxConnections == 25

    @patch.dict(os.environ, {}, clear=True)
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(self):
        """Test that FromEnv uses default values when no environment variables are set."""
        config = DatabaseConfig.FromEnv()

        assert config.databaseType == "postgresql"
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.user == "user"
        assert config.password == "password"
        assert config.database == "miraveja"
        assert config.maxConnections == 10

    @patch.dict(
        os.environ,
        {
            "DATABASE_TYPE": "postgresql",
            "DATABASE_HOST": "localhost",
            "DATABASE_PORT": "5432",
            "DATABASE_USER": "testuser",
            "DATABASE_PASSWORD": "testpass",
            "DATABASE_NAME": "testdb",
        },
    )
    def test_FromEnvWithoutConnectionUrl_ShouldGenerateConnectionUrl(self):
        """Test that FromEnv generates connection URL when not provided in environment."""
        config = DatabaseConfig.FromEnv()

        expected_url = "postgresql://testuser:testpass@localhost:5432/testdb"
        assert config.connectionUrl == expected_url

    def test_ValidateConnectionUrlWithNullValue_ShouldGenerateFromOtherFields(self):
        """Test that connection URL validator generates URL when None is provided."""
        config = DatabaseConfig(
            databaseType="postgresql",
            host="testhost",
            port=5432,
            user="testuser",
            password="testpass",
            database="testdb",
            connectionUrl=None,
        )

        expected_url = "postgresql://testuser:testpass@testhost:5432/testdb"
        assert config.connectionUrl == expected_url

    def test_ValidateConnectionUrlWithExistingValue_ShouldKeepExistingValue(self):
        """Test that connection URL validator keeps existing value when provided."""
        custom_url = "postgresql://custom:url@example.com:5432/customdb"
        config = DatabaseConfig(connectionUrl=custom_url)

        assert config.connectionUrl == custom_url

    def test_InitializeWithNegativePort_ShouldRaiseValidationError(self):
        """Test that initialization raises validation error with negative port."""
        with pytest.raises(ValidationError):
            DatabaseConfig(port=-1, connectionUrl="postgresql://user:password@localhost:-1/miraveja")

    def test_InitializeWithZeroPort_ShouldRaiseValidationError(self):
        """Test that initialization raises validation error with zero port."""
        with pytest.raises(ValidationError):
            DatabaseConfig(port=0, connectionUrl="postgresql://user:password@localhost:0/miraveja")

    def test_InitializeWithNegativeMaxConnections_ShouldRaiseValidationError(self):
        """Test that initialization raises validation error with negative max connections."""
        with pytest.raises(ValidationError):
            DatabaseConfig(maxConnections=-1, connectionUrl="postgresql://user:password@localhost:5432/miraveja")

    def test_InitializeWithZeroMaxConnections_ShouldRaiseValidationError(self):
        """Test that initialization raises validation error with zero max connections."""
        with pytest.raises(ValidationError):
            DatabaseConfig(maxConnections=0, connectionUrl="postgresql://user:password@localhost:5432/miraveja")

    @patch.dict(os.environ, {"DATABASE_PORT": "invalid_port"})
    def test_FromEnvWithInvalidPort_ShouldRaiseValueError(self):
        """Test that FromEnv raises ValueError when DATABASE_PORT is not a valid integer."""
        with pytest.raises(ValueError):
            DatabaseConfig.FromEnv()

    @patch.dict(os.environ, {"DATABASE_MAX_CONNECTIONS": "invalid_max"})
    def test_FromEnvWithInvalidMaxConnections_ShouldRaiseValueError(self):
        """Test that FromEnv raises ValueError when DATABASE_MAX_CONNECTIONS is not a valid integer."""
        with pytest.raises(ValueError):
            DatabaseConfig.FromEnv()

    def test_InitializeWithEmptyStrings_ShouldAllowEmptyValues(self):
        """Test that empty strings are allowed for string fields."""
        config = DatabaseConfig(
            databaseType="", host="", user="", password="", database="", connectionUrl="postgresql://:"
        )

        assert config.databaseType == ""
        assert config.host == ""
        assert config.user == ""
        assert config.password == ""
        assert config.database == ""

    def test_InitializeWithLargePort_ShouldAllowValidPortRange(self):
        """Test that large valid port numbers are accepted."""
        config = DatabaseConfig(port=65535, connectionUrl="postgresql://user:password@localhost:65535/miraveja")

        assert config.port == 65535

    def test_InitializeWithLargeMaxConnections_ShouldAllowLargeValues(self):
        """Test that large max connection values are accepted."""
        config = DatabaseConfig(maxConnections=1000, connectionUrl="postgresql://user:password@localhost:5432/miraveja")

        assert config.maxConnections == 1000

    def test_InitializeWithTooLargePort_ShouldRaiseValidationError(self):
        """Test that initialization raises validation error with port greater than 65535."""
        with pytest.raises(ValidationError):
            DatabaseConfig(port=65536, connectionUrl="postgresql://user:password@localhost:65536/miraveja")

    def test_InitializeWithTooLargeMaxConnections_ShouldRaiseValidationError(self):
        """Test that initialization raises validation error with excessively large max connections."""
        with pytest.raises(ValidationError):
            DatabaseConfig(maxConnections=1001, connectionUrl="postgresql://user:password@localhost:5432/miraveja")
