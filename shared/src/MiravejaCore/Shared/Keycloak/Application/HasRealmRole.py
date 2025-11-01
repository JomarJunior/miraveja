from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator

from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Domain.Services import KeycloakRoleService
from MiravejaCore.Shared.Keycloak.Domain.Interfaces import IKeycloakService
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class HasRealmRoleCommand(BaseModel):
    token: Optional[str] = Field(description="The JWT token to be validated", default=None)
    user: Optional[KeycloakUser] = Field(description="The Keycloak user", default=None)
    role: str = Field(..., description="The realm role to check for")

    @field_validator("token")
    @classmethod
    def ValidateTokenOrUser(cls, v: Optional[str], info: Any) -> Optional[str]:
        if info.data.get("user") is None and v is None:
            raise ValueError("Either token or user must be provided.")
        if info.data.get("user") is not None and v is not None:
            raise ValueError("Only one of token or user should be provided.")
        return v


class HasRealmRoleHandler:
    def __init__(
        self,
        keycloakService: IKeycloakService,
        roleService: KeycloakRoleService,
        logger: ILogger,
    ):
        self.keycloakService = keycloakService
        self.roleService = roleService
        self.logger = logger

    async def Handle(self, command: HasRealmRoleCommand) -> bool:
        self.logger.Info("Checking for realm role...")
        user: KeycloakUser

        if command.user is not None:
            user = command.user
            self.logger.Info(f"User provided: {user.id}")
        else:
            user = await self.keycloakService.ValidateToken(command.token)  # type: ignore
            self.logger.Info(f"Token validated for user: {user.id}")

        hasRole = self.roleService.HasRealmRole(user, command.role)
        if hasRole:
            self.logger.Info(f"User {user.id} has realm role: {command.role}")

        return hasRole
