from typing import Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from MiravejaCore.Shared.Keycloak.Domain.Interfaces import IKeycloakService
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Domain.Services import KeycloakRoleService
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class HasClientRoleCommand(BaseModel):
    token: Optional[str] = Field(description="The JWT token to be validated", default=None)
    user: Optional[KeycloakUser] = Field(description="The Keycloak user", default=None)
    role: str = Field(..., description="The client role to check for")
    client: str = Field(..., description="The client to check the role against")

    @model_validator(mode="after")
    def ValidateTokenOrUser(self) -> Self:
        if self.token is None and self.user is None:
            raise ValueError("Either token or user must be provided.")
        if self.token is not None and self.user is not None:
            raise ValueError("Only one of token or user should be provided.")
        return self


class HasClientRoleHandler:
    def __init__(
        self,
        keycloakService: IKeycloakService,
        roleService: KeycloakRoleService,
        logger: ILogger,
    ):
        self.keycloakService = keycloakService
        self.roleService = roleService
        self.logger = logger

    async def Handle(self, command: HasClientRoleCommand) -> bool:
        self.logger.Info("Checking for client role...")
        user: KeycloakUser

        if command.user is not None:
            user = command.user
            self.logger.Info(f"User provided: {user.id}")
        else:
            user = await self.keycloakService.ValidateToken(command.token)  # type: ignore
            self.logger.Info(f"Token validated for user: {user.id}")

        hasRole = self.roleService.HasClientRole(user=user, role=command.role, client=command.client)
        if hasRole:
            self.logger.Info(f"User {user.id} has client role: {command.role} for client: {command.client}")

        return hasRole
