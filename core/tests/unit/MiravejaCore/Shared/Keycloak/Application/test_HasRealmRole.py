import pytest
from unittest.mock import AsyncMock, Mock
from pydantic import ValidationError

from MiravejaCore.Shared.Keycloak.Application.HasRealmRole import HasRealmRoleCommand, HasRealmRoleHandler
from MiravejaCore.Shared.Keycloak.Domain.Interfaces import IKeycloakService
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Domain.Services import KeycloakRoleService
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class TestHasRealmRoleCommand:
    """Test cases for HasRealmRoleCommand model."""

    def CreateTestKeycloakUser(self) -> KeycloakUser:
        """Create a test Keycloak user."""
        return KeycloakUser(
            id="test-user-123",
            username="testuser",
            email="test@example.com",
            firstName="Test",
            lastName="User",
            emailVerified=True,
            realmRoles=["user", "admin"],
            clientRoles={},
        )

    def test_InitializeWithToken_ShouldSetCorrectValues(self):
        """Test that HasRealmRoleCommand initializes with token."""
        # Arrange
        testToken = "valid.jwt.token"
        testRole = "admin"

        # Act
        command = HasRealmRoleCommand(token=testToken, role=testRole)

        # Assert
        assert command.token == testToken
        assert command.user is None
        assert command.role == testRole

    def test_InitializeWithUser_ShouldSetCorrectValues(self):
        """Test that HasRealmRoleCommand initializes with user."""
        # Arrange
        testUser = self.CreateTestKeycloakUser()
        testRole = "user"

        # Act
        command = HasRealmRoleCommand(user=testUser, role=testRole)

        # Assert
        assert command.token is None
        assert command.user == testUser
        assert command.role == testRole

    def test_InitializeWithoutRole_ShouldRaiseValidationError(self):
        """Test that HasRealmRoleCommand raises validation error without role."""
        # Arrange
        testToken = "valid.jwt.token"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            HasRealmRoleCommand(token=testToken)

        assert "Field required" in str(excInfo.value)

    def test_InitializeWithEmptyRole_ShouldAcceptValue(self):
        """Test that HasRealmRoleCommand accepts empty string role."""
        # Arrange
        testToken = "valid.jwt.token"
        emptyRole = ""

        # Act
        command = HasRealmRoleCommand(token=testToken, role=emptyRole)

        # Assert
        assert command.role == emptyRole

    def test_InitializeWithDifferentRoleFormats_ShouldAcceptValues(self):
        """Test that HasRealmRoleCommand accepts different role formats."""
        # Arrange
        testToken = "valid.jwt.token"
        testRoles = ["admin", "USER", "realm-admin", "realm_admin", "123-role"]

        # Act & Assert
        for role in testRoles:
            command = HasRealmRoleCommand(token=testToken, role=role)
            assert command.role == role

    def test_ValidateTokenOrUser_WithNeitherTokenNorUser_ShouldRaiseValidationError(self):
        """Test that model validator raises error when neither token nor user is provided."""
        # Arrange
        testRole = "admin"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            # Explicitly set both to None to trigger validator
            HasRealmRoleCommand(token=None, user=None, role=testRole)

        assert "Either token or user must be provided" in str(excInfo.value)

    def test_ValidateTokenOrUser_WithBothTokenAndUser_ShouldRaiseValidationError(self):
        """Test that model validator raises error when both token and user are provided."""
        # Arrange
        testToken = "valid.jwt.token"
        testUser = self.CreateTestKeycloakUser()
        testRole = "admin"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            HasRealmRoleCommand(token=testToken, user=testUser, role=testRole)

        assert "Only one of token or user should be provided" in str(excInfo.value)


class TestHasRealmRoleHandler:
    """Test cases for HasRealmRoleHandler service."""

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

    def CreateMockRoleService(self) -> KeycloakRoleService:
        """Create a mock role service for testing."""
        mockRoleService = Mock(spec=KeycloakRoleService)
        return mockRoleService

    def CreateTestKeycloakUser(
        self,
        userId: str = "test-user-123",
        username: str = "testuser",
        realmRoles: list = None,  # type: ignore
    ) -> KeycloakUser:
        """Create a test Keycloak user."""
        if realmRoles is None:
            realmRoles = ["user"]

        return KeycloakUser(
            id=userId,
            username=username,
            email="test@example.com",
            firstName="Test",
            lastName="User",
            emailVerified=True,
            realmRoles=realmRoles,
            clientRoles={},
        )

    def test_InitializeWithValidDependencies_ShouldSetCorrectValues(self):
        """Test that HasRealmRoleHandler initializes with valid dependencies."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()

        # Act
        handler = HasRealmRoleHandler(mockService, mockRoleService, mockLogger)

        # Assert
        assert handler.keycloakService == mockService
        assert handler.roleService == mockRoleService
        assert handler.logger == mockLogger

    @pytest.mark.asyncio
    async def test_HandleWithTokenAndUserHasRole_ShouldReturnTrue(self):
        """Test that Handle returns True when user has realm role (via token)."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(realmRoles=["admin", "user"])

        mockService.ValidateToken = AsyncMock(return_value=testUser)
        mockRoleService.HasRealmRole = Mock(return_value=True)

        handler = HasRealmRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasRealmRoleCommand(token="valid.token", role="admin")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is True
        mockService.ValidateToken.assert_called_once_with("valid.token")  # pylint: disable=no-member
        mockRoleService.HasRealmRole.assert_called_once_with(testUser, "admin")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call("Checking for realm role...")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call(f"Token validated for user: {testUser.id}")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call(f"User {testUser.id} has realm role: admin")  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_HandleWithTokenAndUserDoesNotHaveRole_ShouldReturnFalse(self):
        """Test that Handle returns False when user does not have realm role (via token)."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(realmRoles=["user"])

        mockService.ValidateToken = AsyncMock(return_value=testUser)
        mockRoleService.HasRealmRole = Mock(return_value=False)

        handler = HasRealmRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasRealmRoleCommand(token="valid.token", role="admin")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is False
        mockService.ValidateToken.assert_called_once_with("valid.token")  # pylint: disable=no-member
        mockRoleService.HasRealmRole.assert_called_once_with(testUser, "admin")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call("Checking for realm role...")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call(f"Token validated for user: {testUser.id}")  # pylint: disable=no-member
        # Should not log success message
        assert mockLogger.Info.call_count == 2  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_HandleWithUserObjectAndUserHasRole_ShouldReturnTrue(self):
        """Test that Handle returns True when user has realm role (via user object)."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(userId="user-456", realmRoles=["moderator"])

        mockRoleService.HasRealmRole = Mock(return_value=True)

        handler = HasRealmRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasRealmRoleCommand(user=testUser, role="moderator")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is True
        mockService.ValidateToken.assert_not_called()  # pylint: disable=no-member
        mockRoleService.HasRealmRole.assert_called_once_with(testUser, "moderator")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call("Checking for realm role...")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call("User provided: user-456")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call("User user-456 has realm role: moderator")  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_HandleWithUserObjectAndUserDoesNotHaveRole_ShouldReturnFalse(self):
        """Test that Handle returns False when user does not have realm role (via user object)."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(realmRoles=["user"])

        mockRoleService.HasRealmRole = Mock(return_value=False)

        handler = HasRealmRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasRealmRoleCommand(user=testUser, role="admin")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is False
        mockService.ValidateToken.assert_not_called()  # pylint: disable=no-member
        mockRoleService.HasRealmRole.assert_called_once_with(testUser, "admin")  # pylint: disable=no-member
        assert mockLogger.Info.call_count == 2  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_HandleWithInvalidToken_ShouldPropagateException(self):
        """Test that Handle propagates exception when token validation fails."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testError = Exception("Invalid token")

        mockService.ValidateToken = AsyncMock(side_effect=testError)

        handler = HasRealmRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasRealmRoleCommand(token="invalid.token", role="admin")

        # Act & Assert
        with pytest.raises(Exception) as excInfo:
            await handler.Handle(command)

        assert str(excInfo.value) == "Invalid token"
        mockService.ValidateToken.assert_called_once_with("invalid.token")  # pylint: disable=no-member
        mockRoleService.HasRealmRole.assert_not_called()  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_HandleWithMultipleRoles_ShouldCheckCorrectRole(self):
        """Test that Handle checks the specific role requested."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(realmRoles=["admin", "user", "moderator"])

        mockService.ValidateToken = AsyncMock(return_value=testUser)

        handler = HasRealmRoleHandler(mockService, mockRoleService, mockLogger)

        testCases = [
            ("admin", True),
            ("user", True),
            ("moderator", True),
            ("superadmin", False),
        ]

        # Act & Assert
        for role, expectedResult in testCases:
            mockRoleService.HasRealmRole = Mock(return_value=expectedResult)
            command = HasRealmRoleCommand(token="valid.token", role=role)
            result = await handler.Handle(command)
            assert result == expectedResult
            mockRoleService.HasRealmRole.assert_called_with(testUser, role)

    @pytest.mark.asyncio
    async def test_HandleWithEmptyRealmRoles_ShouldReturnFalse(self):
        """Test that Handle returns False when user has no realm roles."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(realmRoles=[])

        mockRoleService.HasRealmRole = Mock(return_value=False)

        handler = HasRealmRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasRealmRoleCommand(user=testUser, role="any-role")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is False
        mockRoleService.HasRealmRole.assert_called_once_with(testUser, "any-role")  # pylint: disable=no-member
