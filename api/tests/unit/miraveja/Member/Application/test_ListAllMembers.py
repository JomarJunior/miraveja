import pytest
from unittest.mock import MagicMock, Mock
from typing import Type, List

from Miraveja.Member.Application.ListAllMembers import ListAllMembersCommand, ListAllMembersHandler
from Miraveja.Member.Domain.Interfaces import IMemberRepository
from Miraveja.Member.Domain.Models import Member
from Miraveja.Shared.Identifiers.Models import MemberId
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.UnitOfWork.Domain.Interfaces import IUnitOfWorkFactory, IUnitOfWork
from Miraveja.Shared.Utils.Types.Handler import HandlerResponse


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
        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        # Act
        handler = ListAllMembersHandler(mock_uow_factory, mock_repository_type, mock_logger)

        # Assert
        assert handler._databaseUOWFactory == mock_uow_factory
        assert handler._tMemberRepository == mock_repository_type
        assert handler._logger == mock_logger

    def test_HandleWithExistingMembers_ShouldReturnMembersList(self):
        """Test that Handle returns list of members when members exist."""
        # Arrange
        member1_id = MemberId.Generate()
        member2_id = MemberId.Generate()

        member1 = Member.Register(id=member1_id, email="test1@example.com", firstName="John", lastName="Doe")

        member2 = Member.Register(id=member2_id, email="test2@example.com", firstName="Jane", lastName="Smith")

        members_list = [member1, member2]

        mock_uow = Mock(spec=IUnitOfWork)
        mock_repository = Mock(spec=IMemberRepository)
        mock_repository.ListAll.return_value = members_list
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        handler = ListAllMembersHandler(mock_uow_factory, mock_repository_type, mock_logger)
        command = ListAllMembersCommand()

        # Act
        result = handler.Handle(command)

        # Assert
        assert result is not None
        mock_logger.Info.assert_called()
        mock_repository.ListAll.assert_called_once()

    def test_HandleWithNoMembers_ShouldReturnEmptyResponse(self):
        """Test that Handle returns empty response when no members exist."""
        # Arrange
        mock_uow = Mock(spec=IUnitOfWork)
        mock_repository = Mock(spec=IMemberRepository)
        mock_repository.ListAll.return_value = []
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        handler = ListAllMembersHandler(mock_uow_factory, mock_repository_type, mock_logger)
        command = ListAllMembersCommand()

        # Act
        result = handler.Handle(command)

        # Assert
        assert result is not None
        mock_repository.ListAll.assert_called_once()
        mock_logger.Info.assert_called()

    def test_HandleWithValidCommand_ShouldLogInfoMessage(self):
        """Test that Handle logs info message with command details."""
        # Arrange
        mock_uow = Mock(spec=IUnitOfWork)
        mock_repository = Mock(spec=IMemberRepository)
        mock_repository.ListAll.return_value = []
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        handler = ListAllMembersHandler(mock_uow_factory, mock_repository_type, mock_logger)
        command = ListAllMembersCommand()

        # Act
        handler.Handle(command)

        # Assert
        assert mock_logger.Info.call_count >= 1
        logged_message = mock_logger.Info.call_args_list[0][0][0]
        assert "Listing all members with command:" in logged_message
