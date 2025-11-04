import pytest

from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Domain.Services import KeycloakRoleService


class TestKeycloakRoleService:
    """Test cases for KeycloakRoleService domain service."""

    def test_HasRealmRoleWithExistingRole_ShouldReturnTrue(self):
        """Test that HasRealmRole returns True when user has the specified realm role."""
        # Arrange
        user = KeycloakUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            firstName="Test",
            lastName="User",
            emailVerified=True,
            realmRoles=["admin", "user"],
            clientRoles={},
        )
        role_to_check = "admin"

        # Act
        result = KeycloakRoleService.HasRealmRole(user, role_to_check)

        # Assert
        assert result is True

    def test_HasRealmRoleWithNonExistingRole_ShouldReturnFalse(self):
        """Test that HasRealmRole returns False when user does not have the specified realm role."""
        # Arrange
        user = KeycloakUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            firstName="Test",
            lastName="User",
            emailVerified=True,
            realmRoles=["user"],
            clientRoles={},
        )
        role_to_check = "admin"

        # Act
        result = KeycloakRoleService.HasRealmRole(user, role_to_check)

        # Assert
        assert result is False

    def test_HasClientRoleWithExistingClientAndRole_ShouldReturnTrue(self):
        """Test that HasClientRole returns True when user has the specified client role."""
        # Arrange
        user = KeycloakUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            firstName="Test",
            lastName="User",
            emailVerified=True,
            realmRoles=[],
            clientRoles={"api-client": ["read", "write"], "web-client": ["view"]},
        )
        client_name = "api-client"
        role_to_check = "read"

        # Act
        result = KeycloakRoleService.HasClientRole(user, client_name, role_to_check)

        # Assert
        assert result is True

    def test_HasClientRoleWithNonExistingClient_ShouldReturnFalse(self):
        """Test that HasClientRole returns False when client does not exist."""
        # Arrange
        user = KeycloakUser(
            id="user123",
            username="testuser",
            email="test@example.com",
            firstName="Test",
            lastName="User",
            emailVerified=True,
            realmRoles=[],
            clientRoles={"api-client": ["read", "write"]},
        )
        client_name = "nonexistent-client"
        role_to_check = "read"

        # Act
        result = KeycloakRoleService.HasClientRole(user, client_name, role_to_check)

        # Assert
        assert result is False
