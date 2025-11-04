from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class KeycloakRole(BaseModel):
    """Representation of a Keycloak role."""

    id: str = Field(..., description="Role ID")
    name: str = Field(..., description="Role name")
    description: Optional[str] = Field(None, description="Role description")
    composite: bool = Field(False, description="Whether the role is composite")
    clientRole: bool = Field(False, description="Whether the role is a client role")
    containerId: str = Field(..., description="ID of the container (realm or client) that owns the role")


class KeycloakClaims(BaseModel):
    """Claims extracted from a Keycloak token."""

    iss: str = Field(..., description="Issuer")
    sub: str = Field(..., description="Subject (user ID)")
    aud: List[str] = Field(..., description="Audience")
    exp: int = Field(..., description="Expiration time (epoch)")
    iat: int = Field(..., description="Issued at time (epoch)")
    jti: str = Field(..., description="JWT ID")
    typ: Optional[str] = Field(None, description="Token type")
    azp: Optional[str] = Field(None, description="Authorized party (client ID)")
    realmAccess: Optional[Dict[str, Any]] = Field(None, description="Realm access information", alias="realm_access")
    resourceAccess: Optional[Dict[str, Any]] = Field(
        None, description="Resource access information", alias="resource_access"
    )
    scope: Optional[str] = Field(None, description="OAuth 2.0 Scopes")
    isEmailVerified: Optional[bool] = Field(None, description="Whether the email is verified", alias="email_verified")
    email: Optional[str] = Field(None, description="User email")
    name: Optional[str] = Field(None, description="Full name")
    preferredUsername: Optional[str] = Field(None, description="Preferred username", alias="preferred_username")
    givenName: Optional[str] = Field(None, description="Given name", alias="given_name")
    familyName: Optional[str] = Field(None, description="Family name", alias="family_name")


class KeycloakUser(BaseModel):
    """Representation of a Keycloak user."""

    id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: Optional[str] = Field(None, description="Email address")
    firstName: Optional[str] = Field(None, description="First name")
    lastName: Optional[str] = Field(None, description="Last name")
    emailVerified: Optional[bool] = Field(None, description="Whether the email is verified")
    realmRoles: List[str] = Field(default_factory=list, description="Roles assigned at the realm level")
    clientRoles: Dict[str, List[str]] = Field(default_factory=dict, description="Roles assigned at the client level")

    @classmethod
    def FromClaims(cls, claims: KeycloakClaims) -> "KeycloakUser":
        """Create a KeycloakUser instance from KeycloakClaims."""
        realmRoles: List[str] = claims.realmAccess.get("roles", []) if claims.realmAccess else []

        clientRoles: Dict[str, List[str]] = {}
        if claims.resourceAccess:
            for client, access in claims.resourceAccess.items():
                clientRoles[client] = access.get("roles", [])

        return cls(
            id=claims.sub,
            username=claims.preferredUsername or "",
            email=claims.email,
            firstName=claims.givenName,
            lastName=claims.familyName,
            emailVerified=claims.isEmailVerified,
            realmRoles=realmRoles,
            clientRoles=clientRoles,
        )


class KeycloakToken(BaseModel):
    """Representation of a Keycloak token."""

    accessToken: str = Field(..., description="Access token")
    refreshToken: Optional[str] = Field(None, description="Refresh token")
    idToken: Optional[str] = Field(None, description="ID token")
    expiresIn: int = Field(..., description="Access token expiration time in seconds")
    refreshExpiresIn: Optional[int] = Field(None, description="Refresh token expiration time in seconds")
    tokenType: str = Field(..., description="Type of the token, typically 'Bearer'")
