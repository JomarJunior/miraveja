import os
from typing import Optional

from pydantic import BaseModel, Field


class KeycloakConfig(BaseModel):
    """Configuration for Keycloak connection."""

    serverUrl: str = Field(..., description="Keycloak server URL")
    realm: str = Field(..., description="Keycloak realm")
    clientId: str = Field(..., description="Keycloak client ID")
    clientSecret: Optional[str] = Field(None, description="Keycloak client secret, if applicable")
    verifyServerCertificate: bool = Field(True, description="Whether to verify the server's SSL certificate")
    publicKey: Optional[str] = Field(None, description="Public key for the realm, if needed for token verification")
    tokenVerificationAlgorithm: str = Field("RS256", description="Algorithm used for token verification")
    tokenMinimumTimeToLive: int = Field(30, description="Minimum time to live for tokens in seconds")

    @classmethod
    def FromEnv(cls) -> "KeycloakConfig":
        """Create a KeycloakConfig instance from environment variables."""
        return cls(
            serverUrl=os.getenv("KEYCLOAK_SERVER_URL", "http://localhost:8080/auth/"),
            realm=os.getenv("KEYCLOAK_REALM", "miraveja"),
            clientId=os.getenv("KEYCLOAK_CLIENT_ID", "miraveja-client"),
            clientSecret=os.getenv("KEYCLOAK_CLIENT_SECRET", "secret"),
            verifyServerCertificate=os.getenv("KEYCLOAK_VERIFY_SSL", "true").lower() in ("true", "1", "yes"),
            publicKey=os.getenv("KEYCLOAK_PUBLIC_KEY"),
            tokenVerificationAlgorithm=os.getenv("KEYCLOAK_TOKEN_ALGORITHM", "RS256"),
            tokenMinimumTimeToLive=int(os.getenv("KEYCLOAK_TOKEN_MIN_TTL", "30")),
        )
