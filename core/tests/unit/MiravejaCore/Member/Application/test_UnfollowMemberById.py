import pytest
from unittest.mock import Mock, AsyncMock

from MiravejaCore.Member.Application.UnfollowMemberById import UnfollowMemberByIdCommand, UnfollowMemberByIdHandler
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Member.Domain.Models import Member
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory, IDatabaseManager


class TestUnfollowMemberByIdCommand:
    """Test cases for UnfollowMemberByIdCommand model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that UnfollowMemberByIdCommand initializes with valid data."""
        # Arrange
        agentId = MemberId.Generate()
        memberIdToUnfollow = MemberId.Generate()

        # Act
        command = UnfollowMemberByIdCommand(agentId=agentId, memberIdToUnfollow=memberIdToUnfollow)

        # Assert
        assert command.agentId == agentId
        assert command.memberIdToUnfollow == memberIdToUnfollow


class TestUnfollowMemberByIdHandler:
    """Test cases for UnfollowMemberByIdHandler application service."""

    def test_InitializeWithValidDependencies_ShouldSetCorrectProperties(self):
        """Test that UnfollowMemberByIdHandler initializes with valid dependencies."""
        # Arrange
        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)
        mockEventDispatcher = Mock(spec=EventDispatcher)

        # Act
        handler = UnfollowMemberByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )

        # Assert
        assert handler._databaseManagerFactory == mockDatabaseManagerFactory
        assert handler._tMemberRepository == mockRepositoryType
        assert handler._logger == mockLogger
        assert handler._eventDispatcher == mockEventDispatcher

    @pytest.mark.asyncio
    async def test_HandleWithBothMembersExisting_ShouldUnfollowMember(self):
        """Test that Handle unfollows member when both members exist."""
        # Arrange
        agentId = MemberId.Generate()
        memberIdToUnfollow = MemberId.Generate()

        agent = Member.Register(
            id=agentId,
            email="agent@example.com",
            username="agent",
            bio="Test bio",
            avatarId=None,
            coverId=None,
            firstName="Agent",
            lastName="User",
        )

        memberToUnfollow = Member.Register(
            id=memberIdToUnfollow,
            email="member@example.com",
            username="member",
            bio="Test bio",
            avatarId=None,
            coverId=None,
            firstName="Member",
            lastName="User",
        )

        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.FindById.side_effect = [agent, memberToUnfollow]
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)
        mockEventDispatcher = Mock(spec=EventDispatcher)
        mockEventDispatcher.DispatchAll = AsyncMock()

        handler = UnfollowMemberByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = UnfollowMemberByIdCommand(agentId=agentId, memberIdToUnfollow=memberIdToUnfollow)

        # Act
        await handler.Handle(command)

        # Assert
        assert mockRepository.FindById.call_count == 2
        mockRepository.Save.assert_called_once()
        mockDatabaseManager.Commit.assert_called_once()
        mockEventDispatcher.DispatchAll.assert_called_once()
        assert mockLogger.Info.call_count >= 2

    @pytest.mark.asyncio
    async def test_HandleWithAgentNotFound_ShouldNotRaiseException(self):
        """Test that Handle returns gracefully when agent member does not exist."""
        # Arrange
        agentId = MemberId.Generate()
        memberIdToUnfollow = MemberId.Generate()

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

        handler = UnfollowMemberByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = UnfollowMemberByIdCommand(agentId=agentId, memberIdToUnfollow=memberIdToUnfollow)

        # Act
        await handler.Handle(command)

        # Assert
        mockRepository.Save.assert_not_called()
        mockDatabaseManager.Commit.assert_not_called()
        mockLogger.Warning.assert_called_once()

    @pytest.mark.asyncio
    async def test_HandleWithMemberToUnfollowNotFound_ShouldNotRaiseException(self):
        """Test that Handle returns gracefully when member to unfollow does not exist."""
        # Arrange
        agentId = MemberId.Generate()
        memberIdToUnfollow = MemberId.Generate()

        agent = Member.Register(
            id=agentId,
            email="agent@example.com",
            username="agent",
            bio="Test bio",
            avatarId=None,
            coverId=None,
            firstName="Agent",
            lastName="User",
        )

        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.FindById.side_effect = [agent, None]  # Agent exists, member to unfollow does not
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)
        mockEventDispatcher = Mock(spec=EventDispatcher)

        handler = UnfollowMemberByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = UnfollowMemberByIdCommand(agentId=agentId, memberIdToUnfollow=memberIdToUnfollow)

        # Act
        await handler.Handle(command)

        # Assert
        mockRepository.Save.assert_not_called()
        mockDatabaseManager.Commit.assert_not_called()
        assert mockLogger.Warning.call_count == 1

    @pytest.mark.asyncio
    async def test_HandleWithValidMembers_ShouldLogCorrectMessages(self):
        """Test that Handle logs correct info messages."""
        # Arrange
        agentId = MemberId.Generate()
        memberIdToUnfollow = MemberId.Generate()

        agent = Member.Register(
            id=agentId,
            email="agent@example.com",
            username="agent",
            bio="Test bio",
            avatarId=None,
            coverId=None,
            firstName="Agent",
            lastName="User",
        )

        memberToUnfollow = Member.Register(
            id=memberIdToUnfollow,
            email="member@example.com",
            username="member",
            bio="Test bio",
            avatarId=None,
            coverId=None,
            firstName="Member",
            lastName="User",
        )

        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.FindById.side_effect = [agent, memberToUnfollow]
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)
        mockEventDispatcher = Mock(spec=EventDispatcher)
        mockEventDispatcher.DispatchAll = AsyncMock()

        handler = UnfollowMemberByIdHandler(
            mockDatabaseManagerFactory, mockRepositoryType, mockLogger, mockEventDispatcher
        )
        command = UnfollowMemberByIdCommand(agentId=agentId, memberIdToUnfollow=memberIdToUnfollow)

        # Act
        await handler.Handle(command)

        # Assert
        assert mockLogger.Info.call_count >= 3
        firstInfoMessage = mockLogger.Info.call_args_list[0][0][0]
        assert "Unfollowing member by ID with command:" in firstInfoMessage
