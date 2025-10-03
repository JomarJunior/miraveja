import ssl
import time
from typing import Dict, Any, Tuple
import httpx
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, status

from Miraveja.Shared.Keycloak.Domain.Interfaces import IKeycloakService
from Miraveja.Shared.Keycloak.Domain.Models import KeycloakConfig, KeycloakUser, KeycloakClaims

BEARER = "Bearer "


class HttpKeycloakService(IKeycloakService):
    """
    Provides Keycloak authentication services via HTTP.
    """

    def __init__(self, config: KeycloakConfig):
        """Initializes the service with Keycloak configuration."""
        self.config = config
        print(f"Initial config.publicKey: {config.publicKey!r}")
        self._publicKey = config.publicKey
        self._jwksCache = {}
        self._jwksCacheTimestamp = 0
        self._jwksCacheTTL = 3600  # Cache TTL in seconds: 1 hour

    async def FetchPublicKey(self, token: str) -> str:
        """Fetches the public key from Keycloak server."""
        hasValidCachedKey = self._publicKey is not None

        isCacheExpired = (time.time() - self._jwksCacheTimestamp) > self._jwksCacheTTL
        if hasValidCachedKey and not isCacheExpired:
            print("Using cached public key.")
            # Use cached public key if available
            return self._publicKey  # type: ignore

        # Fetch the public key from Keycloak server
        wellKnownUrl = f"{self.config.serverUrl}/realms/{self.config.realm}/.well-known/openid-configuration"

        # Fetch the OpenID configuration to get the JWKS URI
        print(f"Fetching OpenID configuration from {wellKnownUrl}")

        async with httpx.AsyncClient(verify=self.config.verifyServerCertificate) as client:
            response = await client.get(wellKnownUrl)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to fetch OpenID configuration: {response.text}",
                )
            openidConfig = response.json()
            print(f"Fetched OpenID configuration: {openidConfig}")
            jwksUri = openidConfig.get("jwks_uri")
            if not jwksUri:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="JWKS URI not found in OpenID configuration.",
                )

        sslContext = ssl.create_default_context()
        if not self.config.verifyServerCertificate:
            sslContext.check_hostname = False
            sslContext.verify_mode = ssl.CERT_NONE
        else:
            sslContext.verify_mode = ssl.CERT_REQUIRED

        # Use the PyJWKClient to fetch the JWKS URI
        jwksClient = PyJWKClient(
            jwksUri,
            ssl_context=sslContext,
        )

        # Get the signing key for the provided token
        print("Fetching new public key from Keycloak server.")
        signingKey = jwksClient.get_signing_key_from_jwt(token)
        print(f"Fetched signing key: {signingKey}")

        # Cache the fetched public key
        self._publicKey = signingKey.key
        self._jwksCacheTimestamp = time.time()
        print("Fetched and cached new public key.")
        return self._publicKey  # type: ignore

    def _ConvertJwk(self, jwk: Dict[str, Any]) -> str:
        return f"-----BEGIN PUBLIC KEY-----\n{jwk['x5c'][0]}\n-----END PUBLIC KEY-----"

    async def DecodeToken(self, token: str) -> Tuple[KeycloakClaims, Dict[str, Any]]:
        """Decodes and verifies a JWT token."""
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is required.")

        try:
            # Strip the "Bearer " prefix if present
            if token.startswith(BEARER):
                token = token[len(BEARER) :]

            # First decode without verification to check if token is expired
            # This avoids unnecessary public key fetches for expired tokens
            print("Decoding token without verification to check expiration.")
            unverifiedPayload = jwt.decode(token, options={"verify_signature": False})
            print(f"Unverified payload: {unverifiedPayload}")

            # Check expiration
            if "exp" in unverifiedPayload:
                print("Checking token expiration.")
                currentTime = int(time.time())
                if currentTime > unverifiedPayload["exp"]:
                    print("Token has expired.")
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired.")

            # Fetch public key (cached if available)
            publicKey = await self.FetchPublicKey(token)
            print(f"Using public key: {publicKey}")

            # Decode and verify the token
            print("Decoding and verifying token with params:")
            print(f"Token: {token}")
            print(f"Algorithm: {self.config.tokenVerificationAlgorithm}")
            print(f"Audience: {self.config.clientId}")
            payload = jwt.decode(
                token,
                publicKey,
                algorithms=[self.config.tokenVerificationAlgorithm],
                audience=self.config.clientId,
                options={"verify_aud": True},
            )
            claims = KeycloakClaims(**payload)
            return claims, payload

        except jwt.PyJWTError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(error)}"
            ) from error
        except Exception as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Token decoding error: {str(error)}"
            ) from error

    async def ValidateToken(self, token: str) -> KeycloakUser:
        """Validates the token and returns the associated Keycloak user."""
        claims, _ = await self.DecodeToken(token)
        return KeycloakUser.FromClaims(claims)
