import pytest
from unittest.mock import AsyncMock, Mock
from pydantic import ValidationError

from MiravejaCore.Shared.Keycloak.Application.ValidateToken import ValidateTokenCommand, ValidateTokenHandler
from MiravejaCore.Shared.Keycloak.Domain.Interfaces import IKeycloakService
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class TestValidateTokenCommand:
    """Test cases for ValidateTokenCommand model."""

    def test_InitializeWithValidToken_ShouldSetCorrectValues(self):
        """Test that ValidateTokenCommand initializes with valid token."""
        # Arrange
        testToken = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test.token"

        # Act
        command = ValidateTokenCommand(token=testToken)

        # Assert
        assert command.token == testToken

    def test_InitializeWithoutToken_ShouldRaiseValidationError(self):
        """Test that ValidateTokenCommand raises validation error without token."""
        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            ValidateTokenCommand()

        assert "Field required" in str(excInfo.value)

    def test_InitializeWithEmptyToken_ShouldAcceptValue(self):
        """Test that ValidateTokenCommand accepts empty string token."""
        # Arrange
        emptyToken = ""

        # Act
        command = ValidateTokenCommand(token=emptyToken)

        # Assert
        assert command.token == emptyToken

    def test_InitializeWithNoneToken_ShouldRaiseValidationError(self):
        """Test that ValidateTokenCommand raises validation error with None token."""
        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            ValidateTokenCommand(token=None)

        assert "Input should be a valid string" in str(excInfo.value)


class TestValidateTokenHandler:
    """Test cases for ValidateTokenHandler service."""

    def CreateMockKeycloakService(self) -> IKeycloakService:
        """Create a mock Keycloak service for testing."""
        mockService = AsyncMock(spec=IKeycloakService)
        return mockService

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
        email: str = "test@example.com",
    ) -> KeycloakUser:
        """Create a test Keycloak user."""
        return KeycloakUser(
            id=userId,
            username=username,
            email=email,
            firstName="Test",
            lastName="User",
            emailVerified=True,
            realmRoles=["user"],
            clientRoles={},
        )

    def test_InitializeWithValidDependencies_ShouldSetCorrectValues(self):
        """Test that ValidateTokenHandler initializes with valid dependencies."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockLogger = self.CreateMockLogger()

        # Act
        handler = ValidateTokenHandler(mockService, mockLogger)

        # Assert
        assert handler.keycloakService == mockService
        assert handler.logger == mockLogger

    @pytest.mark.asyncio
    async def test_HandleWithValidToken_ShouldReturnUserData(self):
        """Test that Handle returns user data for valid token."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser()
        mockService.ValidateToken = AsyncMock(return_value=testUser)

        handler = ValidateTokenHandler(mockService, mockLogger)
        command = ValidateTokenCommand(token="valid.jwt.token")

        # Act
        result = await handler.Handle(command)

        # Assert
        mockService.ValidateToken.assert_called_once_with("valid.jwt.token")
        assert result["id"] == testUser.id
        assert result["username"] == testUser.username
        assert result["email"] == testUser.email
        assert mockLogger.Info.call_count == 2
        mockLogger.Info.assert_any_call("Validating token...")
        mockLogger.Info.assert_any_call(f"Token is valid for user: {testUser.username} (ID: {testUser.id})")

    @pytest.mark.asyncio
    async def test_HandleWithValidTokenAndUserDetails_ShouldLogCorrectly(self):
        """Test that Handle logs correct information during token validation."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(
            userId="user-456",
            username="johndoe",
            email="john@example.com",
        )
        mockService.ValidateToken = AsyncMock(return_value=testUser)

        handler = ValidateTokenHandler(mockService, mockLogger)
        command = ValidateTokenCommand(token="test.token.here")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result["id"] == "user-456"
        assert result["username"] == "johndoe"
        assert result["email"] == "john@example.com"
        mockLogger.Info.assert_any_call("Token is valid for user: johndoe (ID: user-456)")

    @pytest.mark.asyncio
    async def test_HandleWithInvalidToken_ShouldPropagateException(self):
        """Test that Handle propagates exception when token validation fails."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockLogger = self.CreateMockLogger()
        testError = Exception("Invalid token")
        mockService.ValidateToken = AsyncMock(side_effect=testError)

        handler = ValidateTokenHandler(mockService, mockLogger)
        command = ValidateTokenCommand(token="invalid.token")

        # Act & Assert
        with pytest.raises(Exception) as excInfo:
            await handler.Handle(command)

        assert str(excInfo.value) == "Invalid token"
        mockService.ValidateToken.assert_called_once_with("invalid.token")
        mockLogger.Info.assert_called_once_with("Validating token...")

    @pytest.mark.asyncio
    async def test_HandleWithUserWithoutEmail_ShouldReturnNoneForEmail(self):
        """Test that Handle returns None for email when user has no email."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockLogger = self.CreateMockLogger()
        testUser = KeycloakUser(
            id="user-789",
            username="noemail",
            email=None,
            firstName="No",
            lastName="Email",
            emailVerified=False,
            realmRoles=[],
            clientRoles={},
        )
        mockService.ValidateToken = AsyncMock(return_value=testUser)

        handler = ValidateTokenHandler(mockService, mockLogger)
        command = ValidateTokenCommand(token="token.without.email")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result["email"] is None
        assert result["emailVerified"] is False

    @pytest.mark.asyncio
    async def test_HandleWithUserWithRoles_ShouldIncludeRolesInResult(self):
        """Test that Handle includes realm and client roles in result."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockLogger = self.CreateMockLogger()
        testUser = KeycloakUser(
            id="user-999",
            username="roleuser",
            email="role@example.com",
            firstName="Role",
            lastName="User",
            emailVerified=True,
            realmRoles=["admin", "user"],
            clientRoles={"miraveja-client": ["view", "edit"], "other-client": ["read"]},
        )
        mockService.ValidateToken = AsyncMock(return_value=testUser)

        handler = ValidateTokenHandler(mockService, mockLogger)
        command = ValidateTokenCommand(token="token.with.roles")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result["realmRoles"] == ["admin", "user"]
        assert result["clientRoles"]["miraveja-client"] == ["view", "edit"]
        assert result["clientRoles"]["other-client"] == ["read"]

    @pytest.mark.asyncio
    async def test_HandleWithDifferentTokenFormats_ShouldCallServiceCorrectly(self):
        """Test that Handle passes different token formats correctly to service."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser()
        mockService.ValidateToken = AsyncMock(return_value=testUser)

        handler = ValidateTokenHandler(mockService, mockLogger)

        testTokens = [
            "short.token",
            "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature",
            "Bearer token.with.prefix",
        ]

        # Act & Assert
        for token in testTokens:
            command = ValidateTokenCommand(token=token)
            await handler.Handle(command)
            mockService.ValidateToken.assert_called_with(token)
