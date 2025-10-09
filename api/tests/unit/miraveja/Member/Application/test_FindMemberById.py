import pytest
from unittest.mock import MagicMock, Mock
from typing import Type

from Miraveja.Member.Application.FindMemberById import FindMemberByIdCommand, FindMemberByIdHandler
from Miraveja.Member.Domain.Exceptions import MemberNotFoundException
from Miraveja.Member.Domain.Interfaces import IMemberRepository
from Miraveja.Member.Domain.Models import Member
from Miraveja.Shared.Identifiers.Models import MemberId
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.UnitOfWork.Domain.Interfaces import IUnitOfWorkFactory, IUnitOfWork
from Miraveja.Shared.Utils.Types.Handler import HandlerResponse


class TestFindMemberByIdCommand:
    """Test cases for FindMemberByIdCommand model."""

    def test_InitializeWithValidMemberId_ShouldSetCorrectValues(self):
        """Test that FindMemberByIdCommand initializes with valid member ID."""
        # Arrange
        member_id = MemberId.Generate()

        # Act
        command = FindMemberByIdCommand(memberId=member_id)

        # Assert
        assert command.memberId == member_id

    def test_InitializeWithMemberIdFromString_ShouldCreateCorrectCommand(self):
        """Test that FindMemberByIdCommand can be initialized with member ID from string."""
        # Arrange
        member_id_str = "123e4567-e89b-12d3-a456-426614174000"
        member_id = MemberId(id=member_id_str)

        # Act
        command = FindMemberByIdCommand(memberId=member_id)

        # Assert
        assert command.memberId.id == member_id_str


class TestFindMemberByIdHandler:
    """Test cases for FindMemberByIdHandler application service."""

    def test_InitializeWithValidDependencies_ShouldSetCorrectProperties(self):
        """Test that FindMemberByIdHandler initializes with valid dependencies."""
        # Arrange
        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        # Act
        handler = FindMemberByIdHandler(mock_uow_factory, mock_repository_type, mock_logger)

        # Assert
        assert handler._databaseUOWFactory == mock_uow_factory
        assert handler._tMemberRepository == mock_repository_type
        assert handler._logger == mock_logger

    def test_HandleWithExistingMember_ShouldReturnMemberResponse(self):
        """Test that Handle returns member when member exists."""
        # Arrange
        member_id = MemberId.Generate()
        member = Member.Register(id=member_id, email="test@example.com", firstName="John", lastName="Doe")

        mock_uow = Mock(spec=IUnitOfWork)
        mock_repository = Mock(spec=IMemberRepository)
        mock_repository.FindById.return_value = member
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = Mock(spec=Type[IMemberRepository])
        mock_logger = Mock(spec=ILogger)

        handler = FindMemberByIdHandler(mock_uow_factory, mock_repository_type, mock_logger)
        command = FindMemberByIdCommand(memberId=member_id)

        # Act
        result = handler.Handle(command)

        # Assert
        assert result is not None
        mock_logger.Info.assert_called()
        mock_repository.FindById.assert_called_once_with(member_id)

    def test_HandleWithNonExistingMember_ShouldRaiseMemberNotFoundException(self):
        """Test that Handle raises exception when member does not exist."""
        # Arrange
        member_id = MemberId.Generate()

        mock_uow = Mock(spec=IUnitOfWork)
        mock_repository = Mock(spec=IMemberRepository)
        mock_repository.FindById.return_value = None
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        handler = FindMemberByIdHandler(mock_uow_factory, mock_repository_type, mock_logger)
        command = FindMemberByIdCommand(memberId=member_id)

        # Act & Assert
        with pytest.raises(MemberNotFoundException) as exc_info:
            handler.Handle(command)

        assert exc_info.value.message == f"Member with ID '{member_id.id}' was not found."
        mock_repository.FindById.assert_called_once_with(member_id)

    def test_HandleWithValidCommand_ShouldLogInfoMessage(self):
        """Test that Handle logs info message with command details."""
        # Arrange
        member_id = MemberId.Generate()
        member = Member.Register(id=member_id, email="test@example.com", firstName="John", lastName="Doe")

        mock_uow = Mock(spec=IUnitOfWork)
        mock_repository = Mock(spec=IMemberRepository)
        mock_repository.FindById.return_value = member
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        handler = FindMemberByIdHandler(mock_uow_factory, mock_repository_type, mock_logger)
        command = FindMemberByIdCommand(memberId=member_id)

        # Act
        handler.Handle(command)

        # Assert
        assert mock_logger.Info.call_count >= 1
        logged_message = mock_logger.Info.call_args_list[0][0][0]
        assert "Finding member by ID with command:" in logged_message
