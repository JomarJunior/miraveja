import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from pydantic import ValidationError

from MiravejaCore.Member.Application.RegisterMember import RegisterMemberCommand, RegisterMemberHandler
from MiravejaCore.Member.Domain.Exceptions import MemberAlreadyExistsException
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory, IDatabaseManager


class TestRegisterMemberCommand:
    """Test cases for RegisterMemberCommand model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that RegisterMemberCommand initializes with valid data."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testEmail = "test@example.com"
        testUsername = "testuser"
        testFirstName = "John"
        testLastName = "Doe"

        # Act
        command = RegisterMemberCommand(
            id=testId, email=testEmail, username=testUsername, firstName=testFirstName, lastName=testLastName
        )  # type: ignore

        # Assert
        assert command.id == testId
        assert command.email == testEmail
        assert command.username == testUsername
        assert command.firstName == testFirstName
        assert command.lastName == testLastName
        assert command.bio == ""
        assert command.avatarId is None
        assert command.coverId is None
        assert command.gender is None
        assert command.dateOfBirth is None

    def test_InitializeWithOptionalFields_ShouldSetCorrectValues(self):
        """Test that RegisterMemberCommand initializes with optional fields."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testEmail = "test@example.com"
        testUsername = "testuser"
        testFirstName = "John"
        testLastName = "Doe"
        testBio = "Test bio"
        testAvatarId = 1
        testCoverId = 2
        testGender = "male"
        testDateOfBirth = "1990-01-01"

        # Act
        command = RegisterMemberCommand(
            id=testId,
            email=testEmail,
            username=testUsername,
            firstName=testFirstName,
            lastName=testLastName,
            bio=testBio,
            avatarId=testAvatarId,
            coverId=testCoverId,
            gender=testGender,
            dateOfBirth=testDateOfBirth,
        )

        # Assert
        assert command.bio == testBio
        assert command.avatarId == testAvatarId
        assert command.coverId == testCoverId
        assert command.gender == testGender
        assert command.dateOfBirth == testDateOfBirth

    def test_InitializeWithInvalidEmail_ShouldRaiseValidationError(self):
        """Test that RegisterMemberCommand raises validation error with invalid email."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        invalidEmail = "invalid-email"
        testUsername = "testuser"
        testFirstName = "John"
        testLastName = "Doe"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            RegisterMemberCommand(
                id=testId, email=invalidEmail, username=testUsername, firstName=testFirstName, lastName=testLastName
            )  # type: ignore

        assert "value is not a valid email address" in str(excInfo.value)

    def test_InitializeWithShortUsername_ShouldRaiseValidationError(self):
        """Test that RegisterMemberCommand raises validation error with username too short."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testEmail = "test@example.com"
        shortUsername = "ab"
        testFirstName = "John"
        testLastName = "Doe"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            RegisterMemberCommand(
                id=testId, email=testEmail, username=shortUsername, firstName=testFirstName, lastName=testLastName
            )  # type: ignore

        assert "at least 3 character" in str(excInfo.value)

    def test_InitializeWithLongUsername_ShouldRaiseValidationError(self):
        """Test that RegisterMemberCommand raises validation error with username too long."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testEmail = "test@example.com"
        longUsername = "a" * 42
        testFirstName = "John"
        testLastName = "Doe"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            RegisterMemberCommand(
                id=testId, email=testEmail, username=longUsername, firstName=testFirstName, lastName=testLastName
            )  # type: ignore

        assert "at most 41 character" in str(excInfo.value)

    def test_InitializeWithEmptyFirstName_ShouldRaiseValidationError(self):
        """Test that RegisterMemberCommand raises validation error with empty first name."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testEmail = "test@example.com"
        testUsername = "testuser"
        emptyFirstName = ""
        testLastName = "Doe"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            RegisterMemberCommand(
                id=testId, email=testEmail, username=testUsername, firstName=emptyFirstName, lastName=testLastName
            )  # type: ignore

        assert "at least 1 character" in str(excInfo.value)

    def test_InitializeWithEmptyLastName_ShouldRaiseValidationError(self):
        """Test that RegisterMemberCommand raises validation error with empty last name."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testEmail = "test@example.com"
        testUsername = "testuser"
        testFirstName = "John"
        emptyLastName = ""

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            RegisterMemberCommand(
                id=testId, email=testEmail, username=testUsername, firstName=testFirstName, lastName=emptyLastName
            )  # type: ignore

        assert "at least 1 character" in str(excInfo.value)

    def test_InitializeWithLongBio_ShouldRaiseValidationError(self):
        """Test that RegisterMemberCommand raises validation error with bio too long."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testEmail = "test@example.com"
        testUsername = "testuser"
        testFirstName = "John"
        testLastName = "Doe"
        longBio = "a" * 501

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            RegisterMemberCommand(
                id=testId,
                email=testEmail,
                username=testUsername,
                firstName=testFirstName,
                lastName=testLastName,
                bio=longBio,
            )  # type: ignore

        assert "at most 500 character" in str(excInfo.value)


class TestRegisterMemberHandler:
    """Test cases for RegisterMemberHandler application service."""

    def test_InitializeWithValidDependencies_ShouldSetCorrectProperties(self):
        """Test that RegisterMemberHandler initializes with valid dependencies."""
        # Arrange
        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockRepositoryType = IMemberRepository
        mockEventDispatcher = Mock(spec=EventDispatcher)
        mockLogger = Mock(spec=ILogger)

        # Act
        handler = RegisterMemberHandler(mockDatabaseManagerFactory, mockRepositoryType, mockEventDispatcher, mockLogger)

        # Assert
        assert handler._databaseManagerFactory == mockDatabaseManagerFactory
        assert handler._tMemberRepository == mockRepositoryType
        assert handler._eventDispatcher == mockEventDispatcher
        assert handler._logger == mockLogger

    @pytest.mark.asyncio
    async def test_HandleWithValidCommand_ShouldRegisterMemberSuccessfully(self):
        """Test that Handle registers member successfully with valid command."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testEmail = "test@example.com"
        testUsername = "testuser"
        testFirstName = "John"
        testLastName = "Doe"

        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.MemberExists.return_value = False
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockEventDispatcher = Mock(spec=EventDispatcher)
        mockEventDispatcher.DispatchAll = AsyncMock()
        mockLogger = Mock(spec=ILogger)

        handler = RegisterMemberHandler(mockDatabaseManagerFactory, mockRepositoryType, mockEventDispatcher, mockLogger)
        command = RegisterMemberCommand(
            id=testId, email=testEmail, username=testUsername, firstName=testFirstName, lastName=testLastName
        )  # type: ignore

        # Act
        await handler.Handle(command)

        # Assert
        mockRepository.MemberExists.assert_called_once()
        mockRepository.Save.assert_called_once()
        mockDatabaseManager.Commit.assert_called_once()
        mockEventDispatcher.DispatchAll.assert_called_once()
        assert mockLogger.Info.call_count >= 2

    @pytest.mark.asyncio
    async def test_HandleWithExistingMember_ShouldRaiseMemberAlreadyExistsException(self):
        """Test that Handle raises exception when member already exists."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testEmail = "test@example.com"
        testUsername = "testuser"
        testFirstName = "John"
        testLastName = "Doe"

        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.MemberExists.return_value = True
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockEventDispatcher = Mock(spec=EventDispatcher)
        mockLogger = Mock(spec=ILogger)

        handler = RegisterMemberHandler(mockDatabaseManagerFactory, mockRepositoryType, mockEventDispatcher, mockLogger)
        command = RegisterMemberCommand(
            id=testId, email=testEmail, username=testUsername, firstName=testFirstName, lastName=testLastName
        )  # type: ignore

        # Act & Assert
        with pytest.raises(MemberAlreadyExistsException) as excInfo:
            await handler.Handle(command)

        assert excInfo.value.message == f"Member with ID '{testId}' already exists."
        mockRepository.MemberExists.assert_called_once()
        mockRepository.Save.assert_not_called()
        mockDatabaseManager.Commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_HandleWithValidCommand_ShouldLogCorrectMessages(self):
        """Test that Handle logs correct info and debug messages."""
        # Arrange
        testId = "123e4567-e89b-12d3-a456-426614174000"
        testEmail = "test@example.com"
        testUsername = "testuser"
        testFirstName = "John"
        testLastName = "Doe"

        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.MemberExists.return_value = False
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockEventDispatcher = Mock(spec=EventDispatcher)
        mockEventDispatcher.DispatchAll = AsyncMock()
        mockLogger = Mock(spec=ILogger)

        handler = RegisterMemberHandler(mockDatabaseManagerFactory, mockRepositoryType, mockEventDispatcher, mockLogger)
        command = RegisterMemberCommand(
            id=testId, email=testEmail, username=testUsername, firstName=testFirstName, lastName=testLastName
        )  # type: ignore

        # Act
        await handler.Handle(command)

        # Assert
        assert mockLogger.Info.call_count >= 2
        assert mockLogger.Debug.call_count >= 2

        firstInfoMessage = mockLogger.Info.call_args_list[0][0][0]
        assert "Registering member with command:" in firstInfoMessage
