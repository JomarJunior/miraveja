from fastapi import HTTPException, status


class KeycloakError(HTTPException):
    """Base exception for Keycloak-related errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)


class KeycloakAuthenticationError(KeycloakError):
    """Exception raised for authentication errors."""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class KeycloakAuthorizationError(KeycloakError):
    """Exception raised for authorization errors."""

    def __init__(self, detail: str = "Authorization failed"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)
