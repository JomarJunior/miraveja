from Miraveja.Shared.Keycloak.Domain.Models import KeycloakUser


class KeycloakRoleService:
    @staticmethod
    def HasRealmRole(user: KeycloakUser, role: str) -> bool:
        return role in user.realmRoles

    @staticmethod
    def HasClientRole(user: KeycloakUser, client: str, role: str) -> bool:
        return client in user.clientRoles and role in user.clientRoles[client]
