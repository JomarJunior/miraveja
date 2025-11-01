import pytest
from fastapi import status

from MiravejaApi.Shared.Keycloak.Domain.Exceptions import (
    KeycloakError,
    KeycloakAuthenticationError,
    KeycloakAuthorizationError,
)


class TestKeycloakError:
    """Test cases for KeycloakError base exception."""

    def test_InitializeWithCustomDetail_ShouldSetCorrectValues(self):
        """Test that KeycloakError initializes with custom detail and default status."""
        # Arrange
        custom_detail = "Custom Keycloak error"

        # Act
        exception = KeycloakError(custom_detail)

        # Assert
        assert exception.detail == custom_detail
        assert exception.status_code == status.HTTP_401_UNAUTHORIZED

    def test_InitializeWithCustomDetailAndStatus_ShouldSetCorrectValues(self):
        """Test that KeycloakError initializes with custom detail and status."""
        # Arrange
        custom_detail = "Custom Keycloak error"
        custom_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        # Act
        exception = KeycloakError(custom_detail, custom_status)

        # Assert
        assert exception.detail == custom_detail
        assert exception.status_code == custom_status

    def test_InitializeWithEmptyDetail_ShouldSetEmptyDetail(self):
        """Test that KeycloakError handles empty detail."""
        # Arrange
        empty_detail = ""

        # Act
        exception = KeycloakError(empty_detail)

        # Assert
        assert exception.detail == empty_detail
        assert exception.status_code == status.HTTP_401_UNAUTHORIZED


class TestKeycloakAuthenticationError:
    """Test cases for KeycloakAuthenticationError exception."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that KeycloakAuthenticationError initializes with default values."""
        # Act
        exception = KeycloakAuthenticationError()

        # Assert
        assert exception.detail == "Authentication failed"
        assert exception.status_code == status.HTTP_401_UNAUTHORIZED

    def test_InitializeWithCustomDetail_ShouldSetCustomDetail(self):
        """Test that KeycloakAuthenticationError initializes with custom detail."""
        # Arrange
        custom_detail = "Custom authentication error"

        # Act
        exception = KeycloakAuthenticationError(custom_detail)

        # Assert
        assert exception.detail == custom_detail
        assert exception.status_code == status.HTTP_401_UNAUTHORIZED

    def test_InitializeWithEmptyDetail_ShouldSetEmptyDetail(self):
        """Test that KeycloakAuthenticationError handles empty detail."""
        # Arrange
        empty_detail = ""

        # Act
        exception = KeycloakAuthenticationError(empty_detail)

        # Assert
        assert exception.detail == empty_detail
        assert exception.status_code == status.HTTP_401_UNAUTHORIZED


class TestKeycloakAuthorizationError:
    """Test cases for KeycloakAuthorizationError exception."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that KeycloakAuthorizationError initializes with default values."""
        # Act
        exception = KeycloakAuthorizationError()

        # Assert
        assert exception.detail == "Authorization failed"
        assert exception.status_code == status.HTTP_403_FORBIDDEN

    def test_InitializeWithCustomDetail_ShouldSetCustomDetail(self):
        """Test that KeycloakAuthorizationError initializes with custom detail."""
        # Arrange
        custom_detail = "Custom authorization error"

        # Act
        exception = KeycloakAuthorizationError(custom_detail)

        # Assert
        assert exception.detail == custom_detail
        assert exception.status_code == status.HTTP_403_FORBIDDEN

    def test_InitializeWithEmptyDetail_ShouldSetEmptyDetail(self):
        """Test that KeycloakAuthorizationError handles empty detail."""
        # Arrange
        empty_detail = ""

        # Act
        exception = KeycloakAuthorizationError(empty_detail)

        # Assert
        assert exception.detail == empty_detail
        assert exception.status_code == status.HTTP_403_FORBIDDEN
