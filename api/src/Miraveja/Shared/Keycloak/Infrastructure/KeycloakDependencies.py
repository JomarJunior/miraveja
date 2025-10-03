from Miraveja.Shared.DI.Models import Container
from Miraveja.Shared.Keycloak.Application.HasClientRole import HasClientRoleHandler
from Miraveja.Shared.Keycloak.Application.HasRealmRole import HasRealmRoleHandler
from Miraveja.Shared.Keycloak.Application.ValidateToken import ValidateTokenHandler
from Miraveja.Shared.Keycloak.Domain.Interfaces import IKeycloakService
from Miraveja.Shared.Keycloak.Domain.Models import KeycloakConfig
from Miraveja.Shared.Keycloak.Domain.Services import KeycloakRoleService
from Miraveja.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider
from Miraveja.Shared.Keycloak.Infrastructure.Http.External.Services import HttpKeycloakService


class KeycloakDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        container.RegisterFactories(
            {
                # Services
                KeycloakRoleService.__name__: lambda container: KeycloakRoleService(),
                # Handlers
                ValidateTokenHandler.__name__: lambda container: ValidateTokenHandler(
                    keycloakService=container.Get(IKeycloakService.__name__),
                    logger=container.Get("ILogger"),
                ),
                HasRealmRoleHandler.__name__: lambda container: HasRealmRoleHandler(
                    keycloakService=container.Get(IKeycloakService.__name__),
                    logger=container.Get("ILogger"),
                    roleService=container.Get(KeycloakRoleService.__name__),
                ),
                HasClientRoleHandler.__name__: lambda container: HasClientRoleHandler(
                    keycloakService=container.Get(IKeycloakService.__name__),
                    logger=container.Get("ILogger"),
                    roleService=container.Get(KeycloakRoleService.__name__),
                ),
            }
        )
        container.RegisterSingletons(
            {
                # Services
                # Is a singleton to reuse HTTP sessions and caching
                IKeycloakService.__name__: lambda container: HttpKeycloakService(
                    config=KeycloakConfig.model_validate(container.Get("keycloakConfig")),
                ),
                # Dependency Provider
                # Is a singleton to maintain state if needed in the future
                KeycloakDependencyProvider.__name__: lambda container: KeycloakDependencyProvider(
                    validateTokenHandler=container.Get(ValidateTokenHandler.__name__),
                    hasRealmRoleHandler=container.Get(HasRealmRoleHandler.__name__),
                    hasClientRoleHandler=container.Get(HasClientRoleHandler.__name__),
                    logger=container.Get("ILogger"),
                ),
            }
        )
