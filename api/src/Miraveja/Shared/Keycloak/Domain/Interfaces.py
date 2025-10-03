from abc import ABC, abstractmethod


from Miraveja.Shared.Keycloak.Domain.Models import KeycloakUser, KeycloakConfig


class IKeycloakService(ABC):
    """Provides Keycloak authentication services."""

    @abstractmethod
    def __init__(self, config: KeycloakConfig):
        pass

    @abstractmethod
    async def ValidateToken(self, token: str) -> KeycloakUser:
        pass
