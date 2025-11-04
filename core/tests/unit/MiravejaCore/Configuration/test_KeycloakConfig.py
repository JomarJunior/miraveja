import os
import pytest
from unittest.mock import patch

from MiravejaCore.Shared.Keycloak.Domain.Configuration import KeycloakConfig


class TestKeycloakConfig:
    """Test cases for KeycloakConfig model."""

    @patch.dict(
        os.environ,
        {
            "KEYCLOAK_SERVER_URL": "http://test-keycloak:8080/auth/",
            "KEYCLOAK_REALM": "test-realm",
            "KEYCLOAK_CLIENT_ID": "test-client",
            "KEYCLOAK_CLIENT_SECRET": "test-secret",
            "KEYCLOAK_VERIFY_SSL": "false",
            "KEYCLOAK_PUBLIC_KEY": "test-public-key",
            "KEYCLOAK_TOKEN_ALGORITHM": "HS256",
            "KEYCLOAK_TOKEN_MIN_TTL": "60",
        },
    )
    def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
        """Test that FromEnv creates KeycloakConfig with all environment variables set."""
        config = KeycloakConfig.FromEnv()

        assert isinstance(config, KeycloakConfig)
        assert config.serverUrl == "http://test-keycloak:8080/auth/"
        assert config.realm == "test-realm"
        assert config.clientId == "test-client"
        assert config.clientSecret == "test-secret"
        assert config.verifyServerCertificate is False
        assert config.publicKey == "test-public-key"
        assert config.tokenVerificationAlgorithm == "HS256"
        assert config.tokenMinimumTimeToLive == 60

    @patch.dict(os.environ, {}, clear=True)
    def test_FromEnvWithNoEnvironmentVariables_ShouldUseDefaults(self):
        """Test that FromEnv uses default values when no environment variables are set."""
        config = KeycloakConfig.FromEnv()

        assert isinstance(config, KeycloakConfig)
        assert config.serverUrl == "http://localhost:8080/auth/"
        assert config.realm == "miraveja"
        assert config.clientId == "miraveja-client"
        assert config.clientSecret == "secret"
        assert config.verifyServerCertificate is True
        assert config.publicKey is None
        assert config.tokenVerificationAlgorithm == "RS256"
        assert config.tokenMinimumTimeToLive == 30

    @patch.dict(os.environ, {"KEYCLOAK_VERIFY_SSL": "true"})
    def test_FromEnvWithTrueVerifySSL_ShouldSetVerifyToTrue(self):
        """Test that FromEnv sets verifyServerCertificate to True when KEYCLOAK_VERIFY_SSL is 'true'."""
        config = KeycloakConfig.FromEnv()

        assert config.verifyServerCertificate is True

    @patch.dict(os.environ, {"KEYCLOAK_VERIFY_SSL": "1"})
    def test_FromEnvWithOneVerifySSL_ShouldSetVerifyToTrue(self):
        """Test that FromEnv sets verifyServerCertificate to True when KEYCLOAK_VERIFY_SSL is '1'."""
        config = KeycloakConfig.FromEnv()

        assert config.verifyServerCertificate is True

    @patch.dict(os.environ, {"KEYCLOAK_VERIFY_SSL": "yes"})
    def test_FromEnvWithYesVerifySSL_ShouldSetVerifyToTrue(self):
        """Test that FromEnv sets verifyServerCertificate to True when KEYCLOAK_VERIFY_SSL is 'yes'."""
        config = KeycloakConfig.FromEnv()

        assert config.verifyServerCertificate is True

    @patch.dict(os.environ, {"KEYCLOAK_VERIFY_SSL": "false"})
    def test_FromEnvWithFalseVerifySSL_ShouldSetVerifyToFalse(self):
        """Test that FromEnv sets verifyServerCertificate to False when KEYCLOAK_VERIFY_SSL is 'false'."""
        config = KeycloakConfig.FromEnv()

        assert config.verifyServerCertificate is False

    @patch.dict(os.environ, {"KEYCLOAK_VERIFY_SSL": "0"})
    def test_FromEnvWithZeroVerifySSL_ShouldSetVerifyToFalse(self):
        """Test that FromEnv sets verifyServerCertificate to False when KEYCLOAK_VERIFY_SSL is '0'."""
        config = KeycloakConfig.FromEnv()

        assert config.verifyServerCertificate is False

    @patch.dict(os.environ, {"KEYCLOAK_VERIFY_SSL": "no"})
    def test_FromEnvWithNoVerifySSL_ShouldSetVerifyToFalse(self):
        """Test that FromEnv sets verifyServerCertificate to False when KEYCLOAK_VERIFY_SSL is 'no'."""
        config = KeycloakConfig.FromEnv()

        assert config.verifyServerCertificate is False

    @patch.dict(os.environ, {"KEYCLOAK_VERIFY_SSL": "INVALID"})
    def test_FromEnvWithInvalidVerifySSL_ShouldSetVerifyToFalse(self):
        """Test that FromEnv sets verifyServerCertificate to False when KEYCLOAK_VERIFY_SSL is invalid."""
        config = KeycloakConfig.FromEnv()

        assert config.verifyServerCertificate is False

    @patch.dict(os.environ, {"KEYCLOAK_TOKEN_MIN_TTL": "120"})
    def test_FromEnvWithCustomTokenMinTTL_ShouldSetCorrectValue(self):
        """Test that FromEnv sets correct tokenMinimumTimeToLive when KEYCLOAK_TOKEN_MIN_TTL is set."""
        config = KeycloakConfig.FromEnv()

        assert config.tokenMinimumTimeToLive == 120

    @patch.dict(os.environ, {"KEYCLOAK_TOKEN_MIN_TTL": "invalid"})
    def test_FromEnvWithInvalidTokenMinTTL_ShouldRaiseValueError(self):
        """Test that FromEnv raises ValueError when KEYCLOAK_TOKEN_MIN_TTL is not a valid integer."""
        with pytest.raises(ValueError):
            KeycloakConfig.FromEnv()

    @patch.dict(
        os.environ,
        {
            "KEYCLOAK_SERVER_URL": "",
            "KEYCLOAK_REALM": "",
            "KEYCLOAK_CLIENT_ID": "",
            "KEYCLOAK_CLIENT_SECRET": "",
            "KEYCLOAK_PUBLIC_KEY": "",
            "KEYCLOAK_TOKEN_ALGORITHM": "",
        },
    )
    def test_FromEnvWithEmptyStrings_ShouldAllowEmptyValues(self):
        """Test that FromEnv allows empty strings for optional string fields."""
        config = KeycloakConfig.FromEnv()

        assert config.serverUrl == ""
        assert config.realm == ""
        assert config.clientId == ""
        assert config.clientSecret == ""
        assert config.publicKey == ""
        assert config.tokenVerificationAlgorithm == ""
