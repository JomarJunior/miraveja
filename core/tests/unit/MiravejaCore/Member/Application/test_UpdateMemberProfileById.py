import pytest
from unittest.mock import Mock, AsyncMock
from pydantic import ValidationError

from MiravejaCore.Member.Application.UpdateMemberProfileById import (
    UpdateMemberProfileByIdCommand,
    UpdateMemberProfileByIdHandler,
)
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Member.Domain.Models import Member
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import MemberId, ImageMetadataId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory, IDatabaseManager


class TestUpdateMemberProfileByIdCommand:
    """Test cases for UpdateMemberProfileByIdCommand model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that UpdateMemberProfileByIdCommand initializes with valid data."""
        # Arrange
        memberId = MemberId.Generate()
        bio = "New bio"
        avatarId = ImageMetadataId(id=1)
        coverId = ImageMetadataId(id=2)

        # Act
        command = UpdateMemberProfileByIdCommand(memberId=memberId, bio=bio, avatarId=avatarId, coverId=coverId)

        # Assert
        assert command.memberId == memberId
        assert command.bio == bio
        assert command.avatarId == avatarId
        assert command.coverId == coverId

    def test_InitializeWithLongBio_ShouldRaiseValidationError(self):
        """Test that UpdateMemberProfileByIdCommand raises validation error with bio too long."""
        # Arrange
        memberId = MemberId.Generate()
        longBio = "a" * 501

        # Act & Assert
        with pytest.raises(ValidationError) as excInfo:
            UpdateMemberProfileByIdCommand(memberId=memberId, bio=longBio)

        assert "at most 500 character" in str(excInfo.value)


class TestUpdateMemberProfileByIdHandler:
    """Test cases for UpdateMemberProfileByIdHandler application service."""

    def test_InitializeWithValidDependencies_ShouldSetCorrectProperties(self):
        """Test that UpdateMemberProfileByIdHandler initializes with valid dependencies."""
        # Arrange
        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)
        mockEventDispatcher = Mock(spec=EventDispatcher)

        # Act
        handler = UpdateMemberProfileByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )

        # Assert
        assert handler._databaseManagerFactory == mockDatabaseManagerFactory
        assert handler._tMemberRepository == mockRepositoryType
        assert handler._logger == mockLogger
        assert handler._eventDispatcher == mockEventDispatcher

    @pytest.mark.asyncio
    async def test_HandleWithExistingMember_ShouldUpdateProfile(self):
        """Test that Handle updates member profile when member exists."""
        # Arrange
        memberId = MemberId.Generate()
        member = Member.Register(
            id=memberId,
            email="test@example.com",
            username="testuser",
            bio="Old bio",
            avatarId=None,
            coverId=None,
            firstName="John",
            lastName="Doe",
        )

        newBio = "New bio"
        avatarId = ImageMetadataId(id=1)

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

        handler = UpdateMemberProfileByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = UpdateMemberProfileByIdCommand(memberId=memberId, bio=newBio, avatarId=avatarId, coverId=None)

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

        handler = UpdateMemberProfileByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = UpdateMemberProfileByIdCommand(memberId=memberId, bio="New bio")

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
            bio="Old bio",
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

        handler = UpdateMemberProfileByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = UpdateMemberProfileByIdCommand(memberId=memberId, bio="New bio")

        # Act
        await handler.Handle(command)

        # Assert
        assert mockLogger.Info.call_count >= 3
        firstInfoMessage = mockLogger.Info.call_args_list[0][0][0]
        assert "Updating member profile by ID with command:" in firstInfoMessage
