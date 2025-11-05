import pytest
from unittest.mock import Mock, AsyncMock

from MiravejaCore.Member.Application.DeactivateMemberById import (
    DeactivateMemberByIdCommand,
    DeactivateMemberByIdHandler,
)
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Member.Domain.Models import Member
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory, IDatabaseManager


class TestDeactivateMemberByIdCommand:
    """Test cases for DeactivateMemberByIdCommand model."""

    def test_InitializeWithValidMemberId_ShouldSetCorrectValues(self):
        """Test that DeactivateMemberByIdCommand initializes with valid member ID."""
        # Arrange
        memberId = MemberId.Generate()

        # Act
        command = DeactivateMemberByIdCommand(memberId=memberId)

        # Assert
        assert command.memberId == memberId


class TestDeactivateMemberByIdHandler:
    """Test cases for DeactivateMemberByIdHandler application service."""

    def test_InitializeWithValidDependencies_ShouldSetCorrectProperties(self):
        """Test that DeactivateMemberByIdHandler initializes with valid dependencies."""
        # Arrange
        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)
        mockEventDispatcher = Mock(spec=EventDispatcher)

        # Act
        handler = DeactivateMemberByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )

        # Assert
        assert handler._databaseManagerFactory == mockDatabaseManagerFactory
        assert handler._tMemberRepository == mockRepositoryType
        assert handler._logger == mockLogger
        assert handler._eventDispatcher == mockEventDispatcher

    @pytest.mark.asyncio
    async def test_HandleWithExistingMember_ShouldDeactivateMember(self):
        """Test that Handle deactivates member when member exists."""
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

        handler = DeactivateMemberByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = DeactivateMemberByIdCommand(memberId=memberId)

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

        handler = DeactivateMemberByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = DeactivateMemberByIdCommand(memberId=memberId)

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

        handler = DeactivateMemberByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = DeactivateMemberByIdCommand(memberId=memberId)

        # Act
        await handler.Handle(command)

        # Assert
        assert mockLogger.Info.call_count >= 3
        firstInfoMessage = mockLogger.Info.call_args_list[0][0][0]
        assert "Activating member by ID with command:" in firstInfoMessage
