from abc import ABC, abstractmethod


from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Domain.Configuration import KeycloakConfig


class IKeycloakService(ABC):
    """Provides Keycloak authentication services."""

    @abstractmethod
    def __init__(self, config: KeycloakConfig):
        pass

    @abstractmethod
    async def ValidateToken(self, token: str) -> KeycloakUser:
        pass
