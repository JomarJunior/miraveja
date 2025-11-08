import time
import ssl
from typing import Dict, Any
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from fastapi import HTTPException, status
import jwt
from jwt import PyJWKClient

from MiravejaCore.Shared.Keycloak.Infrastructure.Http.External.Services import HttpKeycloakService, BEARER
from MiravejaCore.Shared.Keycloak.Domain.Configuration import KeycloakConfig
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser, KeycloakClaims


class TestHttpKeycloakService:
    """Test cases for HttpKeycloakService class."""

    @pytest.fixture
    def validConfig(self):
        """Create a valid KeycloakConfig for testing."""
        return KeycloakConfig(
            serverUrl="https://keycloak.example.com",
            realm="test-realm",
            clientId="test-client",
            clientSecret="test-secret",
            verifyServerCertificate=True,
            publicKey=None,
            tokenVerificationAlgorithm="RS256",
            tokenMinimumTimeToLive=30,
        )

    @pytest.fixture
    def validConfigWithPublicKey(self):
        """Create a valid KeycloakConfig with a public key for testing."""
        return KeycloakConfig(
            serverUrl="https://keycloak.example.com",
            realm="test-realm",
            clientId="test-client",
            clientSecret="test-secret",
            verifyServerCertificate=True,
            publicKey="-----BEGIN PUBLIC KEY-----\nMIIBIjANBg...\n-----END PUBLIC KEY-----",
            tokenVerificationAlgorithm="RS256",
            tokenMinimumTimeToLive=30,
        )

    @pytest.fixture
    def validConfigWithoutCertVerification(self):
        """Create a valid KeycloakConfig without certificate verification."""
        return KeycloakConfig(
            serverUrl="https://keycloak.example.com",
            realm="test-realm",
            clientId="test-client",
            clientSecret="test-secret",
            verifyServerCertificate=False,
            publicKey=None,
            tokenVerificationAlgorithm="RS256",
            tokenMinimumTimeToLive=30,
        )

    @pytest.fixture
    def mockHttpxResponse(self):
        """Create a mock httpx response."""
        mockResponse = MagicMock()
        mockResponse.status_code = 200
        mockResponse.json.return_value = {
            "jwks_uri": "https://keycloak.example.com/realms/test-realm/protocol/openid-connect/certs"
        }
        return mockResponse

    @pytest.fixture
    def validTokenPayload(self):
        """Create a valid token payload for testing."""
        currentTime = int(time.time())
        return {
            "iss": "https://keycloak.example.com/realms/test-realm",
            "sub": "user-123",
            "aud": ["test-client"],
            "exp": currentTime + 3600,
            "iat": currentTime,
            "jti": "token-123",
            "typ": "Bearer",
            "azp": "test-client",
            "realm_access": {"roles": ["user", "admin"]},
            "resource_access": {"test-client": {"roles": ["client-admin"]}},
            "scope": "openid profile email",
            "email_verified": True,
            "email": "user@example.com",
            "name": "Test User",
            "preferred_username": "testuser",
            "given_name": "Test",
            "family_name": "User",
        }

    def test_InitializeWithValidConfig_ShouldSetCorrectValues(self, validConfig):
        """Test that HttpKeycloakService initializes with valid config."""
        # Act
        service = HttpKeycloakService(validConfig)

        # Assert
        assert service.config == validConfig
        assert service._publicKey is None
        assert service._jwksCache == {}
        assert service._jwksCacheTimestamp == 0
        assert service._jwksCacheTTL == 3600

    def test_InitializeWithConfigContainingPublicKey_ShouldSetPublicKey(self, validConfigWithPublicKey):
        """Test that HttpKeycloakService initializes with public key from config."""
        # Act
        service = HttpKeycloakService(validConfigWithPublicKey)

        # Assert
        assert service._publicKey == validConfigWithPublicKey.publicKey

    @pytest.mark.asyncio
    async def test_FetchPublicKeyWithCachedKey_ShouldReturnCachedKey(self, validConfigWithPublicKey):
        """Test that FetchPublicKey returns cached key when available and not expired."""
        # Arrange
        service = HttpKeycloakService(validConfigWithPublicKey)
        service._jwksCacheTimestamp = time.time()
        testToken = "test.jwt.token"

        # Act
        result = await service.FetchPublicKey(testToken)

        # Assert
        assert result == validConfigWithPublicKey.publicKey

    @pytest.mark.asyncio
    async def test_FetchPublicKeyWithExpiredCache_ShouldFetchNewKey(self, validConfig, mockHttpxResponse):
        """Test that FetchPublicKey fetches new key when cache is expired."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        service._publicKey = "old-key"
        service._jwksCacheTimestamp = time.time() - 4000  # Expired (> 3600 seconds)
        testToken = "test.jwt.token"
        expectedPublicKey = "-----BEGIN PUBLIC KEY-----\nNEW_KEY\n-----END PUBLIC KEY-----"

        mockSigningKey = MagicMock()
        mockSigningKey.key = expectedPublicKey

        mockJwksClient = MagicMock()
        mockJwksClient.get_signing_key_from_jwt.return_value = mockSigningKey

        mockAsyncClient = AsyncMock()
        mockAsyncClient.__aenter__.return_value = mockAsyncClient
        mockAsyncClient.__aexit__.return_value = None
        mockAsyncClient.get.return_value = mockHttpxResponse

        with patch("httpx.AsyncClient", return_value=mockAsyncClient):
            with patch(
                "MiravejaCore.Shared.Keycloak.Infrastructure.Http.External.Services.PyJWKClient",
                return_value=mockJwksClient,
            ):
                # Act
                result = await service.FetchPublicKey(testToken)

        # Assert
        assert result == expectedPublicKey
        assert service._publicKey == expectedPublicKey
        mockAsyncClient.get.assert_called_once_with(  # pylint: disable=no-member
            "https://keycloak.example.com/realms/test-realm/.well-known/openid-configuration"
        )
        mockJwksClient.get_signing_key_from_jwt.assert_called_once_with(testToken)  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_FetchPublicKeyWithNoCachedKey_ShouldFetchFromServer(self, validConfig, mockHttpxResponse):
        """Test that FetchPublicKey fetches from server when no cached key exists."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "test.jwt.token"
        expectedPublicKey = "-----BEGIN PUBLIC KEY-----\nFETCHED_KEY\n-----END PUBLIC KEY-----"

        mockSigningKey = MagicMock()
        mockSigningKey.key = expectedPublicKey

        mockJwksClient = MagicMock()
        mockJwksClient.get_signing_key_from_jwt.return_value = mockSigningKey

        mockAsyncClient = AsyncMock()
        mockAsyncClient.__aenter__.return_value = mockAsyncClient
        mockAsyncClient.__aexit__.return_value = None
        mockAsyncClient.get.return_value = mockHttpxResponse

        with patch("httpx.AsyncClient", return_value=mockAsyncClient):
            with patch(
                "MiravejaCore.Shared.Keycloak.Infrastructure.Http.External.Services.PyJWKClient",
                return_value=mockJwksClient,
            ):
                # Act
                result = await service.FetchPublicKey(testToken)

        # Assert
        assert result == expectedPublicKey
        assert service._publicKey == expectedPublicKey
        assert service._jwksCacheTimestamp > 0

    @pytest.mark.asyncio
    async def test_FetchPublicKeyWithOpenIdConfigFetchError_ShouldRaiseHTTPException(self, validConfig):
        """Test that FetchPublicKey raises HTTPException when OpenID config fetch fails."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "test.jwt.token"

        mockResponse = MagicMock()
        mockResponse.status_code = 500
        mockResponse.text = "Internal Server Error"

        mockAsyncClient = AsyncMock()
        mockAsyncClient.__aenter__.return_value = mockAsyncClient
        mockAsyncClient.__aexit__.return_value = None
        mockAsyncClient.get.return_value = mockResponse

        with patch("httpx.AsyncClient", return_value=mockAsyncClient):
            # Act & Assert
            with pytest.raises(HTTPException) as excInfo:
                await service.FetchPublicKey(testToken)

            assert excInfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to fetch OpenID configuration" in excInfo.value.detail

    @pytest.mark.asyncio
    async def test_FetchPublicKeyWithMissingJwksUri_ShouldRaiseHTTPException(self, validConfig):
        """Test that FetchPublicKey raises HTTPException when JWKS URI is missing."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "test.jwt.token"

        mockResponse = MagicMock()
        mockResponse.status_code = 200
        mockResponse.json.return_value = {}  # No jwks_uri

        mockAsyncClient = AsyncMock()
        mockAsyncClient.__aenter__.return_value = mockAsyncClient
        mockAsyncClient.__aexit__.return_value = None
        mockAsyncClient.get.return_value = mockResponse

        with patch("httpx.AsyncClient", return_value=mockAsyncClient):
            # Act & Assert
            with pytest.raises(HTTPException) as excInfo:
                await service.FetchPublicKey(testToken)

            assert excInfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "JWKS URI not found" in excInfo.value.detail

    @pytest.mark.asyncio
    async def test_FetchPublicKeyWithCertVerificationDisabled_ShouldUseCorrectSSLContext(
        self, validConfigWithoutCertVerification, mockHttpxResponse
    ):
        """Test that FetchPublicKey uses correct SSL context when cert verification is disabled."""
        # Arrange
        service = HttpKeycloakService(validConfigWithoutCertVerification)
        testToken = "test.jwt.token"
        expectedPublicKey = "-----BEGIN PUBLIC KEY-----\nTEST_KEY\n-----END PUBLIC KEY-----"

        mockSigningKey = MagicMock()
        mockSigningKey.key = expectedPublicKey

        mockJwksClient = MagicMock()
        mockJwksClient.get_signing_key_from_jwt.return_value = mockSigningKey

        mockAsyncClient = AsyncMock()
        mockAsyncClient.__aenter__.return_value = mockAsyncClient
        mockAsyncClient.__aexit__.return_value = None
        mockAsyncClient.get.return_value = mockHttpxResponse

        mockSslContext = MagicMock(spec=ssl.SSLContext)

        with patch("httpx.AsyncClient", return_value=mockAsyncClient):
            with patch("ssl.create_default_context", return_value=mockSslContext):
                with patch(
                    "MiravejaCore.Shared.Keycloak.Infrastructure.Http.External.Services.PyJWKClient",
                    return_value=mockJwksClient,
                ) as mockPyJWKClient:
                    # Act
                    result = await service.FetchPublicKey(testToken)

        # Assert
        assert result == expectedPublicKey
        assert mockSslContext.check_hostname is False
        assert mockSslContext.verify_mode == ssl.CERT_NONE
        mockPyJWKClient.assert_called_once()  # pylint: disable=no-member
        callArgs = mockPyJWKClient.call_args  # pylint: disable=no-member
        assert callArgs[1]["ssl_context"] == mockSslContext

    @pytest.mark.asyncio
    async def test_FetchPublicKeyWithCertVerificationEnabled_ShouldUseCorrectSSLContext(
        self, validConfig, mockHttpxResponse
    ):
        """Test that FetchPublicKey uses correct SSL context when cert verification is enabled."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "test.jwt.token"
        expectedPublicKey = "-----BEGIN PUBLIC KEY-----\nTEST_KEY\n-----END PUBLIC KEY-----"

        mockSigningKey = MagicMock()
        mockSigningKey.key = expectedPublicKey

        mockJwksClient = MagicMock()
        mockJwksClient.get_signing_key_from_jwt.return_value = mockSigningKey

        mockAsyncClient = AsyncMock()
        mockAsyncClient.__aenter__.return_value = mockAsyncClient
        mockAsyncClient.__aexit__.return_value = None
        mockAsyncClient.get.return_value = mockHttpxResponse

        mockSslContext = MagicMock(spec=ssl.SSLContext)

        with patch("httpx.AsyncClient", return_value=mockAsyncClient):
            with patch("ssl.create_default_context", return_value=mockSslContext):
                with patch(
                    "MiravejaCore.Shared.Keycloak.Infrastructure.Http.External.Services.PyJWKClient",
                    return_value=mockJwksClient,
                ) as mockPyJWKClient:
                    # Act
                    result = await service.FetchPublicKey(testToken)

        # Assert
        assert result == expectedPublicKey
        assert mockSslContext.verify_mode == ssl.CERT_REQUIRED
        mockPyJWKClient.assert_called_once()  # pylint: disable=no-member
        callArgs = mockPyJWKClient.call_args  # pylint: disable=no-member
        assert callArgs[1]["ssl_context"] == mockSslContext

    def test_ConvertJwk_ShouldReturnFormattedPublicKey(self, validConfig):
        """Test that _ConvertJwk converts JWK to formatted public key."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testJwk = {"x5c": ["MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."]}

        # Act
        result = service._ConvertJwk(testJwk)

        # Assert
        assert (
            result
            == "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"
        )

    @pytest.mark.asyncio
    async def test_DecodeTokenWithEmptyToken_ShouldRaiseHTTPException(self, validConfig):
        """Test that DecodeToken raises HTTPException with empty token."""
        # Arrange
        service = HttpKeycloakService(validConfig)

        # Act & Assert
        with pytest.raises(HTTPException) as excInfo:
            await service.DecodeToken("")

        assert excInfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Token is required" in excInfo.value.detail

    @pytest.mark.asyncio
    async def test_DecodeTokenWithBearerPrefix_ShouldStripPrefix(self, validConfig, validTokenPayload):
        """Test that DecodeToken strips Bearer prefix from token."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "test.jwt.token"
        bearerToken = f"{BEARER}{testToken}"
        mockPublicKey = "-----BEGIN PUBLIC KEY-----\nTEST_KEY\n-----END PUBLIC KEY-----"

        with patch.object(service, "FetchPublicKey", return_value=mockPublicKey):
            with patch("jwt.decode") as mockDecode:
                mockDecode.return_value = validTokenPayload

                # Act
                claims, payload = await service.DecodeToken(bearerToken)

        # Assert
        assert isinstance(claims, KeycloakClaims)
        assert payload == validTokenPayload
        # Verify jwt.decode was called twice: once unverified, once verified
        assert mockDecode.call_count == 2  # pylint: disable=no-member
        # Second call (verified) should use stripped token
        verifiedCall = mockDecode.call_args_list[1]  # pylint: disable=no-member
        assert verifiedCall[0][0] == testToken

    @pytest.mark.asyncio
    async def test_DecodeTokenWithExpiredToken_ShouldRaiseHTTPException(self, validConfig):
        """Test that DecodeToken raises HTTPException with expired token."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "expired.jwt.token"
        expiredPayload = {
            "exp": int(time.time()) - 3600,  # Expired 1 hour ago
            "sub": "user-123",
        }

        with patch("jwt.decode", return_value=expiredPayload):
            # Act & Assert
            with pytest.raises(HTTPException) as excInfo:
                await service.DecodeToken(testToken)

            # The service catches HTTPException and re-raises within the generic exception handler
            assert "Token has expired" in str(excInfo.value.detail)

    @pytest.mark.asyncio
    async def test_DecodeTokenWithValidToken_ShouldReturnClaimsAndPayload(self, validConfig, validTokenPayload):
        """Test that DecodeToken returns claims and payload with valid token."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "valid.jwt.token"
        mockPublicKey = "-----BEGIN PUBLIC KEY-----\nTEST_KEY\n-----END PUBLIC KEY-----"

        with patch.object(service, "FetchPublicKey", return_value=mockPublicKey):
            with patch("jwt.decode") as mockDecode:
                mockDecode.return_value = validTokenPayload

                # Act
                claims, payload = await service.DecodeToken(testToken)

        # Assert
        assert isinstance(claims, KeycloakClaims)
        assert claims.sub == "user-123"
        assert claims.email == "user@example.com"
        assert payload == validTokenPayload

    @pytest.mark.asyncio
    async def test_DecodeTokenWithJwtError_ShouldRaiseHTTPException(self, validConfig):
        """Test that DecodeToken raises HTTPException on JWT decoding error."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "invalid.jwt.token"
        mockPublicKey = "-----BEGIN PUBLIC KEY-----\nTEST_KEY\n-----END PUBLIC KEY-----"

        with patch.object(service, "FetchPublicKey", return_value=mockPublicKey):
            with patch("jwt.decode") as mockDecode:
                # First call (unverified) succeeds with non-expired token
                currentTime = int(time.time())
                mockDecode.side_effect = [
                    {"exp": currentTime + 3600, "sub": "user-123"},
                    jwt.PyJWTError("Invalid signature"),
                ]

                # Act & Assert
                with pytest.raises(HTTPException) as excInfo:
                    await service.DecodeToken(testToken)

                assert excInfo.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "Invalid token" in excInfo.value.detail

    @pytest.mark.asyncio
    async def test_DecodeTokenWithUnexpectedException_ShouldRaiseHTTPException(self, validConfig):
        """Test that DecodeToken raises HTTPException on unexpected error."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "valid.jwt.token"

        with patch("jwt.decode") as mockDecode:
            # First call (unverified) succeeds with non-expired token
            currentTime = int(time.time())
            mockDecode.side_effect = [
                {"exp": currentTime + 3600, "sub": "user-123"},
                RuntimeError("Unexpected error"),
            ]

            with patch.object(service, "FetchPublicKey", return_value="mock-key"):
                # Act & Assert
                with pytest.raises(HTTPException) as excInfo:
                    await service.DecodeToken(testToken)

                assert excInfo.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                assert "Token decoding error" in excInfo.value.detail

    @pytest.mark.asyncio
    async def test_DecodeTokenWithValidAlgorithmAndAudience_ShouldVerifyCorrectly(self, validConfig, validTokenPayload):
        """Test that DecodeToken verifies token with correct algorithm and audience."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "valid.jwt.token"
        mockPublicKey = "-----BEGIN PUBLIC KEY-----\nTEST_KEY\n-----END PUBLIC KEY-----"

        with patch.object(service, "FetchPublicKey", return_value=mockPublicKey):
            with patch("jwt.decode") as mockDecode:
                mockDecode.return_value = validTokenPayload

                # Act
                await service.DecodeToken(testToken)

        # Assert
        # Second call is the verified decode
        verifiedCall = mockDecode.call_args_list[1]  # pylint: disable=no-member
        assert verifiedCall[1]["algorithms"] == ["RS256"]
        assert verifiedCall[1]["audience"] == "test-client"
        assert verifiedCall[1]["options"] == {"verify_aud": True}

    @pytest.mark.asyncio
    async def test_ValidateTokenWithValidToken_ShouldReturnKeycloakUser(self, validConfig, validTokenPayload):
        """Test that ValidateToken returns KeycloakUser with valid token."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "valid.jwt.token"
        mockPublicKey = "-----BEGIN PUBLIC KEY-----\nTEST_KEY\n-----END PUBLIC KEY-----"

        with patch.object(service, "FetchPublicKey", return_value=mockPublicKey):
            with patch("jwt.decode") as mockDecode:
                mockDecode.return_value = validTokenPayload

                # Act
                user = await service.ValidateToken(testToken)

        # Assert
        assert isinstance(user, KeycloakUser)
        assert user.id == "user-123"
        assert user.username == "testuser"
        assert user.email == "user@example.com"
        assert user.firstName == "Test"
        assert user.lastName == "User"
        assert user.emailVerified is True
        assert "user" in user.realmRoles
        assert "admin" in user.realmRoles
        assert "client-admin" in user.clientRoles.get("test-client", [])

    @pytest.mark.asyncio
    async def test_ValidateTokenWithInvalidToken_ShouldRaiseHTTPException(self, validConfig):
        """Test that ValidateToken raises HTTPException with invalid token."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "invalid.jwt.token"
        mockPublicKey = "-----BEGIN PUBLIC KEY-----\nTEST_KEY\n-----END PUBLIC KEY-----"

        with patch.object(service, "FetchPublicKey", return_value=mockPublicKey):
            with patch("jwt.decode") as mockDecode:
                # First call (unverified) succeeds
                currentTime = int(time.time())
                mockDecode.side_effect = [
                    {"exp": currentTime + 3600, "sub": "user-123"},
                    jwt.PyJWTError("Invalid token"),
                ]

                # Act & Assert
                with pytest.raises(HTTPException) as excInfo:
                    await service.ValidateToken(testToken)

                assert excInfo.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_ValidateTokenWithEmptyToken_ShouldRaiseHTTPException(self, validConfig):
        """Test that ValidateToken raises HTTPException with empty token."""
        # Arrange
        service = HttpKeycloakService(validConfig)

        # Act & Assert
        with pytest.raises(HTTPException) as excInfo:
            await service.ValidateToken("")

        assert excInfo.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Token is required" in excInfo.value.detail

    @pytest.mark.asyncio
    async def test_DecodeTokenWithoutExpirationCheck_ShouldNotValidateExpiration(self, validConfig, validTokenPayload):
        """Test that DecodeToken skips expiration check when exp field is missing in unverified payload."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "valid.jwt.token"
        mockPublicKey = "-----BEGIN PUBLIC KEY-----\nTEST_KEY\n-----END PUBLIC KEY-----"

        # First decode (unverified) returns payload without exp
        unverifiedPayload = {"sub": "user-123"}

        with patch.object(service, "FetchPublicKey", return_value=mockPublicKey):
            with patch("jwt.decode") as mockDecode:
                # First call (unverified) returns payload without exp
                # Second call (verified) returns full payload with exp
                mockDecode.side_effect = [unverifiedPayload, validTokenPayload]

                # Act
                claims, payload = await service.DecodeToken(testToken)

        # Assert
        assert isinstance(claims, KeycloakClaims)
        assert payload == validTokenPayload
        assert claims.exp == validTokenPayload["exp"]

    @pytest.mark.asyncio
    async def test_FetchPublicKeyMultipleTimes_ShouldReuseCache(self, validConfig, mockHttpxResponse):
        """Test that FetchPublicKey reuses cache for multiple requests within TTL."""
        # Arrange
        service = HttpKeycloakService(validConfig)
        testToken = "test.jwt.token"
        expectedPublicKey = "-----BEGIN PUBLIC KEY-----\nCACHED_KEY\n-----END PUBLIC KEY-----"

        mockSigningKey = MagicMock()
        mockSigningKey.key = expectedPublicKey

        mockJwksClient = MagicMock()
        mockJwksClient.get_signing_key_from_jwt.return_value = mockSigningKey

        mockAsyncClient = AsyncMock()
        mockAsyncClient.__aenter__.return_value = mockAsyncClient
        mockAsyncClient.__aexit__.return_value = None
        mockAsyncClient.get.return_value = mockHttpxResponse

        with patch("httpx.AsyncClient", return_value=mockAsyncClient):
            with patch(
                "MiravejaCore.Shared.Keycloak.Infrastructure.Http.External.Services.PyJWKClient",
                return_value=mockJwksClient,
            ):
                # Act - First call fetches from server
                result1 = await service.FetchPublicKey(testToken)
                # Act - Second call should use cache
                result2 = await service.FetchPublicKey(testToken)

        # Assert
        assert result1 == expectedPublicKey
        assert result2 == expectedPublicKey
        # Should only fetch once from server
        mockAsyncClient.get.assert_called_once()  # pylint: disable=no-member
