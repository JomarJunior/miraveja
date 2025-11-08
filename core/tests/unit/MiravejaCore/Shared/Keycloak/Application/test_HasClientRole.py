import pytest
from unittest.mock import AsyncMock, Mock
from pydantic import ValidationError

from MiravejaCore.Shared.Keycloak.Application.HasClientRole import HasClientRoleCommand, HasClientRoleHandler
from MiravejaCore.Shared.Keycloak.Domain.Interfaces import IKeycloakService
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Domain.Services import KeycloakRoleService
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class TestHasClientRoleCommand:
    """Test cases for HasClientRoleCommand model."""

    def CreateTestKeycloakUser(self) -> KeycloakUser:
        """Create a test Keycloak user."""
        return KeycloakUser(
            id="test-user-123",
            username="testuser",
            email="test@example.com",
            firstName="Test",
            lastName="User",
            emailVerified=True,
            realmRoles=["user"],
            clientRoles={"miraveja-client": ["view", "edit"]},
        )

    def test_InitializeWithToken_ShouldSetCorrectValues(self):
        """Test that HasClientRoleCommand initializes with token."""
        # Arrange
        testToken = "valid.jwt.token"
        testRole = "view"
        testClient = "miraveja-client"

        # Act
        command = HasClientRoleCommand(token=testToken, role=testRole, client=testClient)

        # Assert
        assert command.token == testToken
        assert command.user is None
        assert command.role == testRole
        assert command.client == testClient

    def test_InitializeWithUser_ShouldSetCorrectValues(self):
        """Test that HasClientRoleCommand initializes with user."""
        # Arrange
        testUser = self.CreateTestKeycloakUser()
        testRole = "edit"
        testClient = "miraveja-client"

        # Act
        command = HasClientRoleCommand(user=testUser, role=testRole, client=testClient)

        # Assert
        assert command.token is None
        assert command.user == testUser
        assert command.role == testRole
        assert command.client == testClient

    def test_InitializeWithoutRole_ShouldRaiseValidationError(self):
        """Test that HasClientRoleCommand raises validation error without role."""
        # Arrange
        testToken = "valid.jwt.token"
        testClient = "miraveja-client"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            HasClientRoleCommand(token=testToken, client=testClient)

        assert "Field required" in str(excInfo.value)

    def test_InitializeWithoutClient_ShouldRaiseValidationError(self):
        """Test that HasClientRoleCommand raises validation error without client."""
        # Arrange
        testToken = "valid.jwt.token"
        testRole = "view"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            HasClientRoleCommand(token=testToken, role=testRole)

        assert "Field required" in str(excInfo.value)

    def test_InitializeWithEmptyStrings_ShouldAcceptValues(self):
        """Test that HasClientRoleCommand accepts empty string values."""
        # Arrange
        testToken = "valid.jwt.token"
        emptyRole = ""
        emptyClient = ""

        # Act
        command = HasClientRoleCommand(token=testToken, role=emptyRole, client=emptyClient)

        # Assert
        assert command.role == emptyRole
        assert command.client == emptyClient

    def test_InitializeWithDifferentClientAndRoleFormats_ShouldAcceptValues(self):
        """Test that HasClientRoleCommand accepts different client and role formats."""
        # Arrange
        testToken = "valid.jwt.token"
        testCases = [
            ("client-1", "role-1"),
            ("CLIENT_2", "ROLE_2"),
            ("client.three", "role.three"),
            ("123-client", "456-role"),
        ]

        # Act & Assert
        for client, role in testCases:
            command = HasClientRoleCommand(token=testToken, role=role, client=client)
            assert command.role == role
            assert command.client == client

    def test_ValidateTokenOrUser_WithNeitherTokenNorUser_ShouldRaiseValidationError(self):
        """Test that model validator raises error when neither token nor user is provided."""
        # Arrange
        testRole = "view"
        testClient = "miraveja-client"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            # Explicitly set both to None to trigger validator
            HasClientRoleCommand(token=None, user=None, role=testRole, client=testClient)

        assert "Either token or user must be provided" in str(excInfo.value)

    def test_ValidateTokenOrUser_WithBothTokenAndUser_ShouldRaiseValidationError(self):
        """Test that model validator raises error when both token and user are provided."""
        # Arrange
        testToken = "valid.jwt.token"
        testUser = self.CreateTestKeycloakUser()
        testRole = "edit"
        testClient = "miraveja-client"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            HasClientRoleCommand(token=testToken, user=testUser, role=testRole, client=testClient)

        assert "Only one of token or user should be provided" in str(excInfo.value)


class TestHasClientRoleHandler:
    """Test cases for HasClientRoleHandler service."""

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
        clientRoles: dict = None,  # type: ignore
    ) -> KeycloakUser:
        """Create a test Keycloak user."""
        if clientRoles is None:
            clientRoles = {"miraveja-client": ["view"]}

        return KeycloakUser(
            id=userId,
            username=username,
            email="test@example.com",
            firstName="Test",
            lastName="User",
            emailVerified=True,
            realmRoles=["user"],
            clientRoles=clientRoles,
        )

    def test_InitializeWithValidDependencies_ShouldSetCorrectValues(self):
        """Test that HasClientRoleHandler initializes with valid dependencies."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()

        # Act
        handler = HasClientRoleHandler(mockService, mockRoleService, mockLogger)

        # Assert
        assert handler.keycloakService == mockService
        assert handler.roleService == mockRoleService
        assert handler.logger == mockLogger

    @pytest.mark.asyncio
    async def test_HandleWithTokenAndUserHasRole_ShouldReturnTrue(self):
        """Test that Handle returns True when user has client role (via token)."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(clientRoles={"miraveja-client": ["view", "edit"]})

        mockService.ValidateToken = AsyncMock(return_value=testUser)
        mockRoleService.HasClientRole = Mock(return_value=True)

        handler = HasClientRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasClientRoleCommand(token="valid.token", role="view", client="miraveja-client")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is True
        mockService.ValidateToken.assert_called_once_with("valid.token")  # pylint: disable=no-member
        mockRoleService.HasClientRole.assert_called_once_with(  # pylint: disable=no-member
            user=testUser, role="view", client="miraveja-client"
        )
        mockLogger.Info.assert_any_call("Checking for client role...")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call(f"Token validated for user: {testUser.id}")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call(  # pylint: disable=no-member
            f"User {testUser.id} has client role: view for client: miraveja-client"
        )

    @pytest.mark.asyncio
    async def test_HandleWithTokenAndUserDoesNotHaveRole_ShouldReturnFalse(self):
        """Test that Handle returns False when user does not have client role (via token)."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(clientRoles={"miraveja-client": ["view"]})

        mockService.ValidateToken = AsyncMock(return_value=testUser)
        mockRoleService.HasClientRole = Mock(return_value=False)

        handler = HasClientRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasClientRoleCommand(token="valid.token", role="admin", client="miraveja-client")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is False
        mockService.ValidateToken.assert_called_once_with("valid.token")  # pylint: disable=no-member
        mockRoleService.HasClientRole.assert_called_once_with(  # pylint: disable=no-member
            user=testUser, role="admin", client="miraveja-client"
        )
        mockLogger.Info.assert_any_call("Checking for client role...")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call(f"Token validated for user: {testUser.id}")  # pylint: disable=no-member
        # Should not log success message
        assert mockLogger.Info.call_count == 2  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_HandleWithUserObjectAndUserHasRole_ShouldReturnTrue(self):
        """Test that Handle returns True when user has client role (via user object)."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(
            userId="user-456",
            clientRoles={"app-client": ["read", "write"]},
        )

        mockRoleService.HasClientRole = Mock(return_value=True)

        handler = HasClientRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasClientRoleCommand(user=testUser, role="read", client="app-client")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is True
        mockService.ValidateToken.assert_not_called()  # pylint: disable=no-member
        mockRoleService.HasClientRole.assert_called_once_with(  # pylint: disable=no-member
            user=testUser, role="read", client="app-client"
        )
        mockLogger.Info.assert_any_call("Checking for client role...")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call("User provided: user-456")  # pylint: disable=no-member
        mockLogger.Info.assert_any_call(
            "User user-456 has client role: read for client: app-client"
        )  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_HandleWithUserObjectAndUserDoesNotHaveRole_ShouldReturnFalse(self):
        """Test that Handle returns False when user does not have client role (via user object)."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(clientRoles={"miraveja-client": ["view"]})

        mockRoleService.HasClientRole = Mock(return_value=False)

        handler = HasClientRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasClientRoleCommand(user=testUser, role="delete", client="miraveja-client")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is False
        mockService.ValidateToken.assert_not_called()  # pylint: disable=no-member
        mockRoleService.HasClientRole.assert_called_once_with(  # pylint: disable=no-member
            user=testUser, role="delete", client="miraveja-client"
        )
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

        handler = HasClientRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasClientRoleCommand(token="invalid.token", role="view", client="miraveja-client")

        # Act & Assert
        with pytest.raises(Exception) as excInfo:
            await handler.Handle(command)

        assert str(excInfo.value) == "Invalid token"
        mockService.ValidateToken.assert_called_once_with("invalid.token")  # pylint: disable=no-member
        mockRoleService.HasClientRole.assert_not_called()  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_HandleWithMultipleClients_ShouldCheckCorrectClient(self):
        """Test that Handle checks the specific client requested."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(
            clientRoles={
                "client-a": ["view", "edit"],
                "client-b": ["read", "write"],
                "client-c": ["admin"],
            }
        )

        mockService.ValidateToken = AsyncMock(return_value=testUser)

        handler = HasClientRoleHandler(mockService, mockRoleService, mockLogger)

        testCases = [
            ("client-a", "view", True),
            ("client-b", "read", True),
            ("client-c", "admin", True),
            ("client-a", "admin", False),
            ("client-d", "view", False),
        ]

        # Act & Assert
        for client, role, expectedResult in testCases:
            mockRoleService.HasClientRole = Mock(return_value=expectedResult)
            command = HasClientRoleCommand(token="valid.token", role=role, client=client)
            result = await handler.Handle(command)
            assert result == expectedResult
            mockRoleService.HasClientRole.assert_called_with(
                user=testUser, role=role, client=client
            )  # pylint: disable=no-member

    @pytest.mark.asyncio
    async def test_HandleWithEmptyClientRoles_ShouldReturnFalse(self):
        """Test that Handle returns False when user has no client roles."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(clientRoles={})

        mockRoleService.HasClientRole = Mock(return_value=False)

        handler = HasClientRoleHandler(mockService, mockRoleService, mockLogger)
        command = HasClientRoleCommand(user=testUser, role="any-role", client="any-client")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is False
        mockRoleService.HasClientRole.assert_called_once_with(  # pylint: disable=no-member
            user=testUser, role="any-role", client="any-client"
        )

    @pytest.mark.asyncio
    async def test_HandleWithRoleInDifferentClient_ShouldReturnFalse(self):
        """Test that Handle returns False when role exists but in different client."""
        # Arrange
        mockService = self.CreateMockKeycloakService()
        mockRoleService = self.CreateMockRoleService()
        mockLogger = self.CreateMockLogger()
        testUser = self.CreateTestKeycloakUser(clientRoles={"client-a": ["view"], "client-b": ["edit"]})

        mockRoleService.HasClientRole = Mock(return_value=False)

        handler = HasClientRoleHandler(mockService, mockRoleService, mockLogger)
        # Check for "edit" role in "client-a" (but it's in "client-b")
        command = HasClientRoleCommand(user=testUser, role="edit", client="client-a")

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is False
        mockRoleService.HasClientRole.assert_called_once_with(  # pylint: disable=no-member
            user=testUser, role="edit", client="client-a"
        )
