import pytest
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from MiravejaCore.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider
from MiravejaCore.Shared.Keycloak.Application.ValidateToken import ValidateTokenHandler
from MiravejaCore.Shared.Keycloak.Application.HasRealmRole import HasRealmRoleHandler
from MiravejaCore.Shared.Keycloak.Application.HasClientRole import HasClientRoleHandler
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Domain.Exceptions import KeycloakAuthenticationError, KeycloakAuthorizationError
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class TestKeycloakDependencyProvider:
    """Test cases for KeycloakDependencyProvider service."""

    def CreateMockValidateTokenHandler(self) -> ValidateTokenHandler:
        """Create a mock validate token handler for testing."""
        mockHandler = AsyncMock(spec=ValidateTokenHandler)
        return mockHandler

    def CreateMockHasRealmRoleHandler(self) -> HasRealmRoleHandler:
        """Create a mock has realm role handler for testing."""
        mockHandler = AsyncMock(spec=HasRealmRoleHandler)
        return mockHandler

    def CreateMockHasClientRoleHandler(self) -> HasClientRoleHandler:
        """Create a mock has client role handler for testing."""
        mockHandler = AsyncMock(spec=HasClientRoleHandler)
        return mockHandler

    def CreateMockLogger(self) -> ILogger:
        """Create a mock logger for testing."""
        mockLogger = Mock(spec=ILogger)
        mockLogger.Info = Mock()
        mockLogger.Error = Mock()
        mockLogger.Debug = Mock()
        return mockLogger

    def CreateTestKeycloakUser(
        self,
        userId: str = "test-user-123",
        username: str = "testuser",
        realmRoles: list = None,  # type: ignore
        clientRoles: dict = None,  # type: ignore
    ) -> KeycloakUser:
        """Create a test Keycloak user."""
        if realmRoles is None:
            realmRoles = ["user"]
        if clientRoles is None:
            clientRoles = {}

        return KeycloakUser(
            id=userId,
            username=username,
            email="test@example.com",
            firstName="Test",
            lastName="User",
            emailVerified=True,
            realmRoles=realmRoles,
            clientRoles=clientRoles,
        )

    def CreateMockCredentials(self, token: str) -> HTTPAuthorizationCredentials:
        """Create mock HTTP authorization credentials."""
        credentials = Mock(spec=HTTPAuthorizationCredentials)
        credentials.credentials = token
        credentials.scheme = "Bearer"
        return credentials

    def test_InitializeWithValidDependencies_ShouldSetCorrectValues(self):
        """Test that KeycloakDependencyProvider initializes with valid dependencies."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        # Act
        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Assert
        assert provider.validateTokenHandler == mockValidateHandler
        assert provider.hasRealmRoleHandler == mockRealmRoleHandler
        assert provider.hasClientRoleHandler == mockClientRoleHandler
        assert provider.logger == mockLogger
        assert provider.securityScheme is not None

    @pytest.mark.asyncio
    async def test_ValidateTokenWithValidToken_ShouldReturnKeycloakUser(self):
        """Test that ValidateToken returns user for valid token."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser()
        mockValidateHandler.Handle = AsyncMock(return_value=testUser.model_dump())

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        testToken = "valid.jwt.token"

        # Act
        result = await provider.ValidateToken(testToken)

        # Assert
        assert result.id == testUser.id
        assert result.username == testUser.username
        assert result.email == testUser.email
        mockValidateHandler.Handle.assert_called_once()  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_GetCurrentUserWithValidCredentials_ShouldReturnUser(self):
        """Test that GetCurrentUser returns user with valid credentials."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser()
        mockValidateHandler.Handle = AsyncMock(return_value=testUser.model_dump())

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        testCredentials = self.CreateMockCredentials("valid.token")

        # Act
        result = await provider.GetCurrentUser(testCredentials)

        # Assert
        assert result is not None
        assert result.id == testUser.id
        assert result.username == testUser.username

    @pytest.mark.asyncio
    async def test_GetCurrentUserWithNoCredentials_ShouldReturnNone(self):
        """Test that GetCurrentUser returns None without credentials."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Act
        result = await provider.GetCurrentUser(None)

        # Assert
        assert result is None
        mockValidateHandler.Handle.assert_not_called()  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_GetCurrentUserWithInvalidCredentials_ShouldReturnNone(self):
        """Test that GetCurrentUser returns None when validation fails."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        mockValidateHandler.Handle = AsyncMock(side_effect=HTTPException(status_code=401, detail="Invalid token"))

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        testCredentials = self.CreateMockCredentials("invalid.token")

        # Act
        result = await provider.GetCurrentUser(testCredentials)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_GetCurrentUserWebSocketWithValidToken_ShouldReturnUser(self):
        """Test that GetCurrentUserWebSocket returns user with valid token."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser()
        mockValidateHandler.Handle = AsyncMock(return_value=testUser.model_dump())

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        testToken = "valid.websocket.token"

        # Act
        result = await provider.GetCurrentUserWebSocket(testToken)

        # Assert
        assert result is not None
        assert result.id == testUser.id
        assert result.username == testUser.username

    @pytest.mark.asyncio
    async def test_GetCurrentUserWebSocketWithNoToken_ShouldReturnNone(self):
        """Test that GetCurrentUserWebSocket returns None without token."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Act
        result = await provider.GetCurrentUserWebSocket(None)

        # Assert
        assert result is None
        mockValidateHandler.Handle.assert_not_called()  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_GetCurrentUserWebSocketWithInvalidToken_ShouldReturnNone(self):
        """Test that GetCurrentUserWebSocket returns None when validation fails."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        mockValidateHandler.Handle = AsyncMock(side_effect=HTTPException(status_code=401, detail="Invalid token"))

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        testToken = "invalid.websocket.token"

        # Act
        result = await provider.GetCurrentUserWebSocket(testToken)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_RequireAuthenticationWithValidCredentials_ShouldReturnUser(self):
        """Test that RequireAuthentication returns user with valid credentials."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser()
        mockValidateHandler.Handle = AsyncMock(return_value=testUser.model_dump())

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        testCredentials = self.CreateMockCredentials("valid.token")

        # Act
        result = await provider.RequireAuthentication(testCredentials)

        # Assert
        assert result.id == testUser.id
        assert result.username == testUser.username

    @pytest.mark.asyncio
    async def test_RequireAuthenticationWithNoCredentials_ShouldRaiseException(self):
        """Test that RequireAuthentication raises exception without credentials."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Act & Assert
        with pytest.raises(KeycloakAuthenticationError) as excInfo:
            await provider.RequireAuthentication(None)

        assert "Authorization credentials are missing" in str(excInfo.value.detail)

    @pytest.mark.asyncio
    async def test_RequireAuthenticationWithInvalidCredentials_ShouldRaiseException(self):
        """Test that RequireAuthentication raises exception with invalid credentials."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        mockValidateHandler.Handle = AsyncMock(side_effect=HTTPException(status_code=401, detail="Token expired"))

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        testCredentials = self.CreateMockCredentials("expired.token")

        # Act & Assert
        with pytest.raises(KeycloakAuthenticationError) as excInfo:
            await provider.RequireAuthentication(testCredentials)

        assert "Token expired" in str(excInfo.value.detail)

    @pytest.mark.asyncio
    async def test_RequireAuthenticationWebSocketWithValidToken_ShouldReturnUser(self):
        """Test that RequireAuthenticationWebSocket returns user with valid token."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser()
        mockValidateHandler.Handle = AsyncMock(return_value=testUser.model_dump())

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        testToken = "valid.websocket.token"

        # Act
        result = await provider.RequireAuthenticationWebSocket(testToken)

        # Assert
        assert result.id == testUser.id
        assert result.username == testUser.username

    @pytest.mark.asyncio
    async def test_RequireAuthenticationWebSocketWithNoToken_ShouldRaiseException(self):
        """Test that RequireAuthenticationWebSocket raises exception without token."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Act & Assert
        with pytest.raises(KeycloakAuthenticationError) as excInfo:
            await provider.RequireAuthenticationWebSocket(None)

        assert "Authorization token is missing" in str(excInfo.value.detail)

    @pytest.mark.asyncio
    async def test_RequireAuthenticationWebSocketWithInvalidToken_ShouldRaiseException(self):
        """Test that RequireAuthenticationWebSocket raises exception with invalid token."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        mockValidateHandler.Handle = AsyncMock(
            side_effect=HTTPException(status_code=401, detail="Invalid WebSocket token")
        )

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        testToken = "invalid.websocket.token"

        # Act & Assert
        with pytest.raises(KeycloakAuthenticationError) as excInfo:
            await provider.RequireAuthenticationWebSocket(testToken)

        assert "Invalid WebSocket token" in str(excInfo.value.detail)

    @pytest.mark.asyncio
    async def test_RequireRealmRolesWithUserHavingRoles_ShouldReturnUser(self):
        """Test that RequireRealmRoles returns user when user has required roles."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser(realmRoles=["admin", "user"])
        mockRealmRoleHandler.Handle = AsyncMock(return_value=True)

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Create the dependency function
        requireAdminRole = provider.RequireRealmRoles(["admin"])

        # Act
        result = await requireAdminRole(testUser)

        # Assert
        assert result.id == testUser.id
        mockRealmRoleHandler.Handle.assert_called_once()  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_RequireRealmRolesWithUserMissingRoles_ShouldRaiseException(self):
        """Test that RequireRealmRoles raises exception when user lacks required roles."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser(realmRoles=["user"])
        mockRealmRoleHandler.Handle = AsyncMock(return_value=False)

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Create the dependency function
        requireAdminRole = provider.RequireRealmRoles(["admin"])

        # Act & Assert
        with pytest.raises(KeycloakAuthorizationError) as excInfo:
            await requireAdminRole(testUser)

        assert "User lacks required realm role: admin" in str(excInfo.value.detail)

    @pytest.mark.asyncio
    async def test_RequireRealmRolesWithMultipleRoles_ShouldCheckAllRoles(self):
        """Test that RequireRealmRoles checks all required roles."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser(realmRoles=["admin", "moderator"])
        mockRealmRoleHandler.Handle = AsyncMock(return_value=True)

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Create the dependency function
        requireMultipleRoles = provider.RequireRealmRoles(["admin", "moderator"])

        # Act
        result = await requireMultipleRoles(testUser)

        # Assert
        assert result.id == testUser.id
        assert mockRealmRoleHandler.Handle.call_count == 2  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_RequireClientRolesWithUserHavingRoles_ShouldReturnUser(self):
        """Test that RequireClientRoles returns user when user has required roles."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser(clientRoles={"miraveja-client": ["view", "edit"]})
        mockClientRoleHandler.Handle = AsyncMock(return_value=True)

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Create the dependency function
        requireViewRole = provider.RequireClientRoles("miraveja-client", ["view"])

        # Act
        result = await requireViewRole(testUser)

        # Assert
        assert result.id == testUser.id
        mockClientRoleHandler.Handle.assert_called_once()  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_RequireClientRolesWithUserMissingRoles_ShouldRaiseException(self):
        """Test that RequireClientRoles raises exception when user lacks required roles."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser(clientRoles={"miraveja-client": ["view"]})
        mockClientRoleHandler.Handle = AsyncMock(return_value=False)

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Create the dependency function
        requireAdminRole = provider.RequireClientRoles("miraveja-client", ["admin"])

        # Act & Assert
        with pytest.raises(KeycloakAuthorizationError) as excInfo:
            await requireAdminRole(testUser)

        assert "User lacks required client role: admin for client: miraveja-client" in str(excInfo.value.detail)

    @pytest.mark.asyncio
    async def test_RequireClientRolesWithMultipleRoles_ShouldCheckAllRoles(self):
        """Test that RequireClientRoles checks all required roles."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser(clientRoles={"app-client": ["read", "write", "delete"]})
        mockClientRoleHandler.Handle = AsyncMock(return_value=True)

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Create the dependency function
        requireMultipleRoles = provider.RequireClientRoles("app-client", ["read", "write"])

        # Act
        result = await requireMultipleRoles(testUser)

        # Assert
        assert result.id == testUser.id
        assert mockClientRoleHandler.Handle.call_count == 2  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_RequireAdminPrivilegesWithAdminUser_ShouldReturnUser(self):
        """Test that RequireAdminPrivileges returns user when user has admin role."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser(realmRoles=["admin", "user"])
        mockRealmRoleHandler.Handle = AsyncMock(return_value=True)

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Create the dependency function
        requireAdmin = provider.RequireAdminPrivileges()

        # Act
        result = await requireAdmin(testUser)

        # Assert
        assert result.id == testUser.id
        mockRealmRoleHandler.Handle.assert_called_once()  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_RequireAdminPrivilegesWithNonAdminUser_ShouldRaiseException(self):
        """Test that RequireAdminPrivileges raises exception when user lacks admin role."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser(realmRoles=["user"])
        mockRealmRoleHandler.Handle = AsyncMock(return_value=False)

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Create the dependency function
        requireAdmin = provider.RequireAdminPrivileges()

        # Act & Assert
        with pytest.raises(KeycloakAuthorizationError) as excInfo:
            await requireAdmin(testUser)

        assert "User lacks required admin privileges" in str(excInfo.value.detail)

    @pytest.mark.asyncio
    async def test_GetOptionalUserWithUser_ShouldReturnUser(self):
        """Test that GetOptionalUser returns user when provided."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        testUser = self.CreateTestKeycloakUser()

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Create the dependency function
        getOptional = provider.GetOptionalUser()

        # Act
        result = await getOptional(testUser)

        # Assert
        assert result is not None
        assert result.id == testUser.id

    @pytest.mark.asyncio
    async def test_GetOptionalUserWithNone_ShouldReturnNone(self):
        """Test that GetOptionalUser returns None when no user provided."""
        # Arrange
        mockValidateHandler = self.CreateMockValidateTokenHandler()
        mockRealmRoleHandler = self.CreateMockHasRealmRoleHandler()
        mockClientRoleHandler = self.CreateMockHasClientRoleHandler()
        mockLogger = self.CreateMockLogger()

        provider = KeycloakDependencyProvider(
            mockValidateHandler,
            mockRealmRoleHandler,
            mockClientRoleHandler,
            mockLogger,
        )

        # Create the dependency function
        getOptional = provider.GetOptionalUser()

        # Act
        result = await getOptional(None)

        # Assert
        assert result is None
