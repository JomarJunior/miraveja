import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from pydantic import ValidationError

from MiravejaCore.Member.Application.UpdateMemberIdentityById import (
    UpdateMemberIdentityByIdComand,
    UpdateMemberIdentityByIdHandler,
)
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Member.Domain.Models import Member
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory, IDatabaseManager


class TestUpdateMemberIdentityByIdComand:
    """Test cases for UpdateMemberIdentityByIdComand model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that UpdateMemberIdentityByIdComand initializes with valid data."""
        # Arrange
        memberId = MemberId.Generate()
        firstName = "Jane"
        lastName = "Smith"
        gender = "female"
        dateOfBirth = datetime(1990, 1, 1)

        # Act
        command = UpdateMemberIdentityByIdComand(
            memberId=memberId, firstName=firstName, lastName=lastName, gender=gender, dateOfBirth=dateOfBirth
        )

        # Assert
        assert command.memberId == memberId
        assert command.firstName == firstName
        assert command.lastName == lastName
        assert command.gender == gender
        assert command.dateOfBirth == dateOfBirth

    def test_InitializeWithEmptyFirstName_ShouldRaiseValidationError(self):
        """Test that UpdateMemberIdentityByIdComand raises validation error with empty first name."""
        # Arrange
        memberId = MemberId.Generate()
        emptyFirstName = ""
        lastName = "Smith"

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            UpdateMemberIdentityByIdComand(memberId=memberId, firstName=emptyFirstName, lastName=lastName)

        assert "at least 1 character" in str(excInfo.value)

    def test_InitializeWithLongGender_ShouldRaiseValidationError(self):
        """Test that UpdateMemberIdentityByIdComand raises validation error with gender too long."""
        # Arrange
        memberId = MemberId.Generate()
        firstName = "Jane"
        lastName = "Smith"
        longGender = "a" * 21

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            UpdateMemberIdentityByIdComand(memberId=memberId, firstName=firstName, lastName=lastName, gender=longGender)

        assert "at most 20 character" in str(excInfo.value)


class TestUpdateMemberIdentityByIdHandler:
    """Test cases for UpdateMemberIdentityByIdHandler application service."""

    def test_InitializeWithValidDependencies_ShouldSetCorrectProperties(self):
        """Test that UpdateMemberIdentityByIdHandler initializes with valid dependencies."""
        # Arrange
        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)
        mockEventDispatcher = Mock(spec=EventDispatcher)

        # Act
        handler = UpdateMemberIdentityByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )

        # Assert
        assert handler._databaseManagerFactory == mockDatabaseManagerFactory
        assert handler._tMemberRepository == mockRepositoryType
        assert handler._logger == mockLogger
        assert handler._eventDispatcher == mockEventDispatcher

    @pytest.mark.asyncio
    async def test_HandleWithExistingMember_ShouldUpdateIdentity(self):
        """Test that Handle updates member identity when member exists."""
        # Arrange
        memberId = MemberId.Generate()
        member = Member.Register(
            id=memberId,
            email="test@example.com",
            username="testuser",
            bio="Test bio",
            avatarId=None,
            coverId=None,
            firstName="John",
            lastName="Doe",
        )

        newFirstName = "Jane"
        newLastName = "Smith"
        newGender = "female"
        newDateOfBirth = datetime(1990, 1, 1)

        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.FindById.return_value = member
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)
        mockEventDispatcher = Mock(spec=EventDispatcher)
        mockEventDispatcher.DispatchAll = AsyncMock()

        handler = UpdateMemberIdentityByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = UpdateMemberIdentityByIdComand(
            memberId=memberId,
            firstName=newFirstName,
            lastName=newLastName,
            gender=newGender,
            dateOfBirth=newDateOfBirth,
        )

        # Act
        await handler.Handle(command)

        # Assert
        mockRepository.FindById.assert_called_once_with(memberId)
        mockRepository.Save.assert_called_once()
        mockDatabaseManager.Commit.assert_called_once()
        mockEventDispatcher.DispatchAll.assert_called_once()
        assert mockLogger.Info.call_count >= 2

    @pytest.mark.asyncio
    async def test_HandleWithNonExistingMember_ShouldNotRaiseException(self):
        """Test that Handle returns gracefully when member does not exist."""
        # Arrange
        memberId = MemberId.Generate()

        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.FindById.return_value = None
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)
        mockEventDispatcher = Mock(spec=EventDispatcher)

        handler = UpdateMemberIdentityByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = UpdateMemberIdentityByIdComand(memberId=memberId, firstName="Jane", lastName="Smith")

        # Act
        await handler.Handle(command)

        # Assert
        mockRepository.FindById.assert_called_once_with(memberId)
        mockRepository.Save.assert_not_called()
        mockDatabaseManager.Commit.assert_not_called()
        mockLogger.Warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleWithValidMember_ShouldLogCorrectMessages(self):
        """Test that Handle logs correct info messages."""
        # Arrange
        memberId = MemberId.Generate()
        member = Member.Register(
            id=memberId,
            email="test@example.com",
            username="testuser",
            bio="Test bio",
            avatarId=None,
            coverId=None,
            firstName="John",
            lastName="Doe",
        )

        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.FindById.return_value = member
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)
        mockEventDispatcher = Mock(spec=EventDispatcher)
        mockEventDispatcher.DispatchAll = AsyncMock()

        handler = UpdateMemberIdentityByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = UpdateMemberIdentityByIdComand(memberId=memberId, firstName="Jane", lastName="Smith")

        # Act
        await handler.Handle(command)

        # Assert
        assert mockLogger.Info.call_count >= 3
        firstInfoMessage = mockLogger.Info.call_args_list[0][0][0]
        assert "Updating member identity by ID with command:" in firstInfoMessage
