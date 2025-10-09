import pytest
from unittest.mock import MagicMock, Mock
from typing import Type
from pydantic import ValidationError

from Miraveja.Member.Application.RegisterMember import RegisterMemberCommand, RegisterMemberHandler
from Miraveja.Member.Domain.Exceptions import MemberAlreadyExistsException
from Miraveja.Member.Domain.Interfaces import IMemberRepository
from Miraveja.Member.Domain.Models import Member
from Miraveja.Shared.Identifiers.Models import MemberId
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.UnitOfWork.Domain.Interfaces import IUnitOfWorkFactory, IUnitOfWork


class TestRegisterMemberCommand:
    """Test cases for RegisterMemberCommand model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that RegisterMemberCommand initializes with valid data."""
        # Arrange
        test_id = "123e4567-e89b-12d3-a456-426614174000"
        test_email = "test@example.com"
        test_first_name = "John"
        test_last_name = "Doe"

        # Act
        command = RegisterMemberCommand(
            id=test_id, email=test_email, firstName=test_first_name, lastName=test_last_name
        )

        # Assert
        assert command.id == test_id
        assert command.email == test_email
        assert command.firstName == test_first_name
        assert command.lastName == test_last_name

    def test_InitializeWithInvalidEmail_ShouldRaiseValidationError(self):
        """Test that RegisterMemberCommand raises validation error with invalid email."""
        # Arrange
        test_id = "123e4567-e89b-12d3-a456-426614174000"
        invalid_email = "invalid-email"
        test_first_name = "John"
        test_last_name = "Doe"

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegisterMemberCommand(id=test_id, email=invalid_email, firstName=test_first_name, lastName=test_last_name)

        assert "value is not a valid email address" in str(exc_info.value)

    def test_InitializeWithEmptyFirstName_ShouldRaiseValidationError(self):
        """Test that RegisterMemberCommand raises validation error with empty first name."""
        # Arrange
        test_id = "123e4567-e89b-12d3-a456-426614174000"
        test_email = "test@example.com"
        empty_first_name = ""
        test_last_name = "Doe"

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegisterMemberCommand(id=test_id, email=test_email, firstName=empty_first_name, lastName=test_last_name)

        assert "String should have at least 1 character" in str(exc_info.value)

    def test_InitializeWithEmptyLastName_ShouldRaiseValidationError(self):
        """Test that RegisterMemberCommand raises validation error with empty last name."""
        # Arrange
        test_id = "123e4567-e89b-12d3-a456-426614174000"
        test_email = "test@example.com"
        test_first_name = "John"
        empty_last_name = ""

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            RegisterMemberCommand(id=test_id, email=test_email, firstName=test_first_name, lastName=empty_last_name)

        assert "String should have at least 1 character" in str(exc_info.value)


class TestRegisterMemberHandler:
    """Test cases for RegisterMemberHandler application service."""

    def test_InitializeWithValidDependencies_ShouldSetCorrectProperties(self):
        """Test that RegisterMemberHandler initializes with valid dependencies."""
        # Arrange
        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        # Act
        handler = RegisterMemberHandler(mock_uow_factory, mock_repository_type, mock_logger)

        # Assert
        assert handler._databaseUOWFactory == mock_uow_factory
        assert handler._tMemberRepository == mock_repository_type
        assert handler._logger == mock_logger

    def test_HandleWithValidCommand_ShouldRegisterMemberSuccessfully(self):
        """Test that Handle registers member successfully with valid command."""
        # Arrange
        test_id = "123e4567-e89b-12d3-a456-426614174000"
        test_email = "test@example.com"
        test_first_name = "John"
        test_last_name = "Doe"

        mock_uow = Mock(spec=IUnitOfWork)
        mock_repository = Mock(spec=IMemberRepository)
        mock_repository.MemberExists.return_value = False
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        handler = RegisterMemberHandler(mock_uow_factory, mock_repository_type, mock_logger)
        command = RegisterMemberCommand(
            id=test_id, email=test_email, firstName=test_first_name, lastName=test_last_name
        )

        # Act
        handler.Handle(command)

        # Assert
        mock_repository.MemberExists.assert_called_once()
        mock_repository.Save.assert_called_once()
        mock_uow.Commit.assert_called_once()
        mock_logger.Info.assert_called()

    def test_HandleWithExistingMember_ShouldRaiseMemberAlreadyExistsException(self):
        """Test that Handle raises exception when member already exists."""
        # Arrange
        test_id = "123e4567-e89b-12d3-a456-426614174000"
        test_email = "test@example.com"
        test_first_name = "John"
        test_last_name = "Doe"

        mock_uow = Mock(spec=IUnitOfWork)
        mock_repository = Mock(spec=IMemberRepository)
        mock_repository.MemberExists.return_value = True
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        handler = RegisterMemberHandler(mock_uow_factory, mock_repository_type, mock_logger)
        command = RegisterMemberCommand(
            id=test_id, email=test_email, firstName=test_first_name, lastName=test_last_name
        )

        # Act & Assert
        with pytest.raises(MemberAlreadyExistsException) as exc_info:
            handler.Handle(command)

        assert exc_info.value.message == f"Member with ID '{test_id}' already exists."
        mock_repository.MemberExists.assert_called_once()
        mock_repository.Save.assert_not_called()
        mock_uow.Commit.assert_not_called()

    def test_HandleWithValidCommand_ShouldLogCorrectMessages(self):
        """Test that Handle logs correct info and debug messages."""
        # Arrange
        test_id = "123e4567-e89b-12d3-a456-426614174000"
        test_email = "test@example.com"
        test_first_name = "John"
        test_last_name = "Doe"

        mock_uow = Mock(spec=IUnitOfWork)
        mock_repository = Mock(spec=IMemberRepository)
        mock_repository.MemberExists.return_value = False
        mock_uow.GetRepository.return_value = mock_repository
        mock_uow.__enter__ = Mock(return_value=mock_uow)
        mock_uow.__exit__ = Mock(return_value=None)

        mock_uow_factory = Mock(spec=IUnitOfWorkFactory)
        mock_uow_factory.Create.return_value = mock_uow
        mock_repository_type = IMemberRepository
        mock_logger = Mock(spec=ILogger)

        handler = RegisterMemberHandler(mock_uow_factory, mock_repository_type, mock_logger)
        command = RegisterMemberCommand(
            id=test_id, email=test_email, firstName=test_first_name, lastName=test_last_name
        )

        # Act
        handler.Handle(command)

        # Assert
        assert mock_logger.Info.call_count >= 2  # Should log start and end messages
        assert mock_logger.Debug.call_count >= 2  # Should log debug messages

        # Check that the first Info call contains the registration message
        first_info_message = mock_logger.Info.call_args_list[0][0][0]
        assert "Registering member with command:" in first_info_message
