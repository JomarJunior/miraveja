import pytest
from unittest.mock import Mock

from MiravejaCore.Member.Application.ListAllMembers import ListAllMembersCommand, ListAllMembersHandler
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Member.Domain.Models import Member
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory, IDatabaseManager


class TestListAllMembersCommand:
    """Test cases for ListAllMembersCommand model."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
        """Test that ListAllMembersCommand initializes with default values."""
        # Act
        command = ListAllMembersCommand()

        # Assert - should have proper initialization without parameters
        assert command is not None


class TestListAllMembersHandler:
    """Test cases for ListAllMembersHandler application service."""

    def test_InitializeWithValidDependencies_ShouldSetCorrectProperties(self):
        """Test that ListAllMembersHandler initializes with valid dependencies."""
        # Arrange
        mock_uow_factory = Mock(spec=IDatabaseManagerFactory)
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        # Act
        handler = ListAllMembersHandler(mock_uow_factory, mock_repository_type, mock_logger)

        # Assert
        assert handler._databaseManagerFactory == mock_uow_factory
        assert handler._tMemberRepository == mock_repository_type
        assert handler._logger == mock_logger

    @pytest.mark.asyncio
    async def test_HandleWithExistingMembers_ShouldReturnMembersList(self):
        """Test that Handle returns list of members when members exist."""
        # Arrange
        member1Id = MemberId.Generate()
        member2Id = MemberId.Generate()

        member1 = Member.Register(
            id=member1Id,
            email="test1@example.com",
            username="user1",
            bio="Test bio 1",
            avatarId=None,
            coverId=None,
            firstName="John",
            lastName="Doe",
        )

        member2 = Member.Register(
            id=member2Id,
            email="test2@example.com",
            username="user2",
            bio="Test bio 2",
            avatarId=None,
            coverId=None,
            firstName="Jane",
            lastName="Smith",
        )

        membersList = [member1, member2]

        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.ListAll.return_value = membersList
        mockRepository.Count.return_value = 2
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)

        handler = ListAllMembersHandler(mockDatabaseManagerFactory, mockRepositoryType, mockLogger)
        command = ListAllMembersCommand()

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is not None
        assert "items" in result
        assert "pagination" in result
        assert len(result["items"]) == 2
        mockRepository.ListAll.assert_called_once()
        mockRepository.Count.assert_called_once()
        mockLogger.Info.assert_called()

    @pytest.mark.asyncio
    async def test_HandleWithNoMembers_ShouldReturnEmptyResponse(self):
        """Test that Handle returns empty response when no members exist."""
        # Arrange
        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.ListAll.return_value = []
        mockRepository.Count.return_value = 0
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)

        handler = ListAllMembersHandler(mockDatabaseManagerFactory, mockRepositoryType, mockLogger)
        command = ListAllMembersCommand()

        # Act
        result = await handler.Handle(command)

        # Assert
        assert result is not None
        assert "items" in result
        assert len(result["items"]) == 0
        mockRepository.ListAll.assert_called_once()
        mockRepository.Count.assert_called_once()
        mockLogger.Info.assert_called()

    @pytest.mark.asyncio
    async def test_HandleWithValidCommand_ShouldLogInfoMessage(self):
        """Test that Handle logs info message with command details."""
        # Arrange
        mockDatabaseManager = Mock(spec=IDatabaseManager)
        mockRepository = Mock(spec=IMemberRepository)
        mockRepository.ListAll.return_value = []
        mockRepository.Count.return_value = 0
        mockDatabaseManager.GetRepository.return_value = mockRepository
        mockDatabaseManager.__enter__ = Mock(return_value=mockDatabaseManager)
        mockDatabaseManager.__exit__ = Mock(return_value=None)

        mockDatabaseManagerFactory = Mock(spec=IDatabaseManagerFactory)
        mockDatabaseManagerFactory.Create.return_value = mockDatabaseManager
        mockRepositoryType = IMemberRepository
        mockLogger = Mock(spec=ILogger)

        handler = ListAllMembersHandler(mockDatabaseManagerFactory, mockRepositoryType, mockLogger)
        command = ListAllMembersCommand()

        # Act
        await handler.Handle(command)

        # Assert
        assert mockLogger.Info.call_count >= 1
        loggedMessage = mockLogger.Info.call_args_list[0][0][0]
        assert "Listing all members with command:" in loggedMessage
