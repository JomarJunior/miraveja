"""Unit tests for KeycloakDependencies module."""

from unittest.mock import MagicMock

import pytest

from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Keycloak.Application.HasClientRole import HasClientRoleHandler
from MiravejaCore.Shared.Keycloak.Application.HasRealmRole import HasRealmRoleHandler
from MiravejaCore.Shared.Keycloak.Application.ValidateToken import ValidateTokenHandler
from MiravejaCore.Shared.Keycloak.Domain.Configuration import KeycloakConfig
from MiravejaCore.Shared.Keycloak.Domain.Interfaces import IKeycloakService
from MiravejaCore.Shared.Keycloak.Domain.Services import KeycloakRoleService
from MiravejaCore.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider
from MiravejaCore.Shared.Keycloak.Infrastructure.Http.External.Services import HttpKeycloakService
from MiravejaCore.Shared.Keycloak.Infrastructure.KeycloakDependencies import KeycloakDependencies
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class TestKeycloakDependencies:
    """Test cases for KeycloakDependencies configuration."""

    def test_RegisterDependencies_ShouldRegisterKeycloakRoleService(self):
        """Test that RegisterDependencies registers KeycloakRoleService as factory."""
        container = Container()

        # Setup mock dependencies
        container.instances["keycloakConfig"] = {
            "serverUrl": "http://localhost:8080",
            "realm": "test-realm",
            "clientId": "test-client",
            "clientSecret": "test-secret",
        }
        container.instances[ILogger.__name__] = MagicMock(spec=ILogger)

        # Register dependencies
        KeycloakDependencies.RegisterDependencies(container)

        # Verify service is registered
        service = container.Get(KeycloakRoleService.__name__)
        assert service is not None
        assert isinstance(service, KeycloakRoleService)

    def test_RegisterDependencies_ShouldRegisterHttpKeycloakServiceAsSingleton(self):
        """Test that RegisterDependencies registers HttpKeycloakService as singleton."""
        container = Container()

        # Setup mock dependencies
        keycloak_config = {
            "serverUrl": "http://keycloak.example.com:8080",
            "realm": "production",
            "clientId": "my-app",
            "clientSecret": "secret123",
        }
        container.instances["keycloakConfig"] = keycloak_config
        container.instances[ILogger.__name__] = MagicMock(spec=ILogger)

        # Register dependencies
        KeycloakDependencies.RegisterDependencies(container)

        # Get service twice
        service1 = container.Get(IKeycloakService.__name__)
        service2 = container.Get(IKeycloakService.__name__)

        # Verify it's a singleton (same instance)
        assert service1 is service2
        assert isinstance(service1, HttpKeycloakService)

    def test_RegisterDependencies_ShouldRegisterValidateTokenHandler(self):
        """Test that RegisterDependencies registers ValidateTokenHandler with dependencies."""
        container = Container()

        # Setup mock dependencies
        mock_logger = MagicMock(spec=ILogger)
        mock_keycloak_service = MagicMock(spec=IKeycloakService)
        container.instances["keycloakConfig"] = {
            "serverUrl": "http://localhost:8080",
            "realm": "test",
            "clientId": "client",
            "clientSecret": "secret",
        }
        container.instances[ILogger.__name__] = mock_logger
        container.instances[IKeycloakService.__name__] = mock_keycloak_service

        # Register dependencies
        KeycloakDependencies.RegisterDependencies(container)

        # Verify handler is registered with correct dependencies
        handler = container.Get(ValidateTokenHandler.__name__)
        assert handler is not None
        assert isinstance(handler, ValidateTokenHandler)
        assert handler.keycloakService == mock_keycloak_service
        assert handler.logger == mock_logger

    def test_RegisterDependencies_ShouldRegisterHasRealmRoleHandler(self):
        """Test that RegisterDependencies registers HasRealmRoleHandler."""
        container = Container()

        # Setup mock dependencies
        mock_logger = MagicMock(spec=ILogger)
        container.instances["keycloakConfig"] = {
            "serverUrl": "http://localhost:8080",
            "realm": "test",
            "clientId": "client",
            "clientSecret": "secret",
        }
        container.instances[ILogger.__name__] = mock_logger

        # Register dependencies
        KeycloakDependencies.RegisterDependencies(container)

        # Verify handler is registered
        handler = container.Get(HasRealmRoleHandler.__name__)
        assert handler is not None
        assert isinstance(handler, HasRealmRoleHandler)
        assert handler.logger == mock_logger
        assert handler.roleService is not None

    def test_RegisterDependencies_ShouldRegisterHasClientRoleHandler(self):
        """Test that RegisterDependencies registers HasClientRoleHandler."""
        container = Container()

        # Setup mock dependencies
        mock_logger = MagicMock(spec=ILogger)
        container.instances["keycloakConfig"] = {
            "serverUrl": "http://localhost:8080",
            "realm": "test",
            "clientId": "client",
            "clientSecret": "secret",
        }
        container.instances[ILogger.__name__] = mock_logger

        # Register dependencies
        KeycloakDependencies.RegisterDependencies(container)

        # Verify handler is registered
        handler = container.Get(HasClientRoleHandler.__name__)
        assert handler is not None
        assert isinstance(handler, HasClientRoleHandler)
        assert handler.logger == mock_logger
        assert handler.roleService is not None

    def test_RegisterDependencies_ShouldRegisterKeycloakDependencyProviderAsSingleton(self):
        """Test that RegisterDependencies registers KeycloakDependencyProvider as singleton."""
        container = Container()

        # Setup mock dependencies
        container.instances["keycloakConfig"] = {
            "serverUrl": "http://localhost:8080",
            "realm": "test",
            "clientId": "client",
            "clientSecret": "secret",
        }
        container.instances[ILogger.__name__] = MagicMock(spec=ILogger)

        # Register dependencies
        KeycloakDependencies.RegisterDependencies(container)

        # Get provider twice
        provider1 = container.Get(KeycloakDependencyProvider.__name__)
        provider2 = container.Get(KeycloakDependencyProvider.__name__)

        # Verify it's a singleton
        assert provider1 is provider2
        assert isinstance(provider1, KeycloakDependencyProvider)

    def test_RegisterDependencies_KeycloakDependencyProvider_ShouldInjectAllHandlers(self):
        """Test that KeycloakDependencyProvider receives all handlers."""
        container = Container()

        # Setup mock dependencies
        container.instances["keycloakConfig"] = {
            "serverUrl": "http://localhost:8080",
            "realm": "test",
            "clientId": "client",
            "clientSecret": "secret",
        }
        container.instances[ILogger.__name__] = MagicMock(spec=ILogger)

        # Register dependencies
        KeycloakDependencies.RegisterDependencies(container)

        # Get provider and verify handlers were injected
        provider = container.Get(KeycloakDependencyProvider.__name__)
        assert provider.validateTokenHandler is not None
        assert provider.hasRealmRoleHandler is not None
        assert provider.hasClientRoleHandler is not None
        assert provider.logger is not None

    def test_RegisterDependencies_Handlers_ShouldBeFactories(self):
        """Test that handlers are registered as factories (new instance each time)."""
        container = Container()

        # Setup mock dependencies
        container.instances["keycloakConfig"] = {
            "serverUrl": "http://localhost:8080",
            "realm": "test",
            "clientId": "client",
            "clientSecret": "secret",
        }
        container.instances[ILogger.__name__] = MagicMock(spec=ILogger)

        # Register dependencies
        KeycloakDependencies.RegisterDependencies(container)

        # Get handler twice
        handler1 = container.Get(ValidateTokenHandler.__name__)
        handler2 = container.Get(ValidateTokenHandler.__name__)

        # Verify they are different instances (factory pattern)
        assert handler1 is not handler2

    def test_RegisterDependencies_HttpKeycloakService_ShouldUseKeycloakConfig(self):
        """Test that HttpKeycloakService uses KeycloakConfig from container."""
        container = Container()

        # Setup dependencies with specific config
        keycloak_config_dict = {
            "serverUrl": "https://auth.example.com",
            "realm": "my-realm",
            "clientId": "my-client-id",
            "clientSecret": "super-secret-123",
        }
        container.instances["keycloakConfig"] = keycloak_config_dict
        container.instances[ILogger.__name__] = MagicMock(spec=ILogger)

        # Register dependencies
        KeycloakDependencies.RegisterDependencies(container)

        # Get service and verify it was created (config is private, so just verify creation)
        service = container.Get(IKeycloakService.__name__)
        assert service is not None
        assert isinstance(service, HttpKeycloakService)
