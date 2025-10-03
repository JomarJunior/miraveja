from typing import Dict, Any
from pydantic import BaseModel, Field

from Miraveja.Shared.Keycloak.Domain.Interfaces import IKeycloakService
from Miraveja.Shared.Keycloak.Domain.Models import KeycloakUser
from Miraveja.Shared.Logging.Interfaces import ILogger


class ValidateTokenCommand(BaseModel):
    token: str = Field(..., description="The JWT token to be validated")


class ValidateTokenHandler:
    def __init__(self, keycloakService: IKeycloakService, logger: ILogger):
        self.keycloakService = keycloakService
        self.logger = logger

    async def Handle(self, command: ValidateTokenCommand) -> Dict[str, Any]:
        self.logger.Info("Validating token...")
        user: KeycloakUser = await self.keycloakService.ValidateToken(command.token)

        self.logger.Info(f"Token is valid for user: {user.username} (ID: {user.id})")

        return user.model_dump()
