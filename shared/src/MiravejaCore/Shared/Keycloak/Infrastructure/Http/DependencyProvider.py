from typing import List, Optional, Callable

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Domain.Exceptions import KeycloakAuthenticationError, KeycloakAuthorizationError
from MiravejaCore.Shared.Keycloak.Application.ValidateToken import ValidateTokenHandler, ValidateTokenCommand
from MiravejaCore.Shared.Keycloak.Application.HasRealmRole import HasRealmRoleCommand, HasRealmRoleHandler
from MiravejaCore.Shared.Keycloak.Application.HasClientRole import HasClientRoleCommand, HasClientRoleHandler
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class KeycloakDependencyProvider:
    """
    Provides dependency injection for Keycloak authentication and authorization.
    """

    def __init__(
        self,
        validateTokenHandler: ValidateTokenHandler,
        hasRealmRoleHandler: HasRealmRoleHandler,
        hasClientRoleHandler: HasClientRoleHandler,
        logger: ILogger,
    ):
        """Initializes the provider with Keycloak configuration."""
        self.securityScheme = HTTPBearer(auto_error=False)
        self.validateTokenHandler = validateTokenHandler
        self.hasRealmRoleHandler = hasRealmRoleHandler
        self.hasClientRoleHandler = hasClientRoleHandler
        self.logger = logger

    async def GetCurrentUser(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
    ) -> Optional[KeycloakUser]:
        """Extract and validate the user from request token."""
        if not credentials:
            return None

        try:
            command = ValidateTokenCommand(token=credentials.credentials)
            user: KeycloakUser = KeycloakUser.model_validate(await self.validateTokenHandler.Handle(command))
            return user
        except HTTPException:
            return None

    async def RequireAuthentication(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> KeycloakUser:
        """Require authentication for the current user."""
        if not credentials:
            raise KeycloakAuthenticationError("Authorization credentials are missing.")

        try:
            command = ValidateTokenCommand(token=credentials.credentials)
            user: KeycloakUser = KeycloakUser.model_validate(await self.validateTokenHandler.Handle(command))
            return user
        except HTTPException as error:
            raise KeycloakAuthenticationError(str(error.detail)) from error

    def RequireRealmRoles(self, roles: List[str]) -> Callable[[KeycloakUser], KeycloakUser]:
        """Require specific realm roles for the current user."""

        async def Dependency(user: KeycloakUser = Depends(self.RequireAuthentication)) -> KeycloakUser:
            for role in roles:
                command = HasRealmRoleCommand(user=user, role=role)
                if not await self.hasRealmRoleHandler.Handle(command):
                    raise KeycloakAuthorizationError(f"User lacks required realm role: {role}")
            return user

        return Dependency  # type: ignore

    def RequireClientRoles(self, client: str, roles: List[str]) -> Callable[[KeycloakUser], KeycloakUser]:
        """Require specific client roles for the current user."""

        async def Dependency(user: KeycloakUser = Depends(self.RequireAuthentication)) -> KeycloakUser:
            for role in roles:
                command = HasClientRoleCommand(user=user, role=role, client=client)
                if not await self.hasClientRoleHandler.Handle(command):
                    raise KeycloakAuthorizationError(f"User lacks required client role: {role} for client: {client}")
            return user

        return Dependency  # type: ignore

    def RequireAdminPrivileges(self) -> Callable[[KeycloakUser], KeycloakUser]:
        """Require admin privileges for the current user."""

        async def Dependency(user: KeycloakUser = Depends(self.RequireAuthentication)) -> KeycloakUser:
            command = HasRealmRoleCommand(user=user, role="admin")
            if not await self.hasRealmRoleHandler.Handle(command):
                raise KeycloakAuthorizationError("User lacks required admin privileges.")
            return user

        return Dependency  # type: ignore

    def GetOptionalUser(self) -> Callable[[Optional[KeycloakUser]], Optional[KeycloakUser]]:
        """Get the optional current user."""

        async def Dependency(user: Optional[KeycloakUser] = Depends(self.GetCurrentUser)) -> Optional[KeycloakUser]:
            return user

        return Dependency  # type: ignore
