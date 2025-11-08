import pytest

from MiravejaCore.Member.Domain.Exceptions import (
    InvalidEmailException,
    MissingEmailException,
    MissingFirstNameException,
    MissingLastNameException,
    MissingUsernameException,
    MemberNotFoundException,
    MemberAlreadyExistsException,
)
from MiravejaCore.Shared.Identifiers.Models import MemberId


class TestInvalidEmailException:
    """Test cases for InvalidEmailException."""

    def test_InitializeWithInvalidEmail_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message for invalid email."""
        invalid_email = "not-an-email"

        exception = InvalidEmailException(invalid_email)

        expected_message = f"The email '{invalid_email}' is not valid."
        assert str(exception) == expected_message
        assert exception.code == 400

    def test_InitializeWithEmptyEmail_ShouldSetCorrectMessage(self):
        """Test that exception handles empty email correctly."""
        empty_email = ""

        exception = InvalidEmailException(empty_email)

        expected_message = f"The email '{empty_email}' is not valid."
        assert str(exception) == expected_message
        assert exception.code == 400

    def test_InitializeWithSpecialCharacters_ShouldSetCorrectMessage(self):
        """Test that exception handles special characters in email."""
        special_email = "test@<script>alert('xss')</script>"

        exception = InvalidEmailException(special_email)

        expected_message = f"The email '{special_email}' is not valid."
        assert str(exception) == expected_message
        assert exception.code == 400


class TestMissingEmailException:
    """Test cases for MissingEmailException."""

    def test_Initialize_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message."""
        exception = MissingEmailException()

        expected_message = "Email is required but was not provided."
        assert str(exception) == expected_message
        assert exception.code == 400

    def test_RaiseException_ShouldBeRaisable(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(MissingEmailException) as exc_info:
            raise MissingEmailException()

        assert "Email is required but was not provided." in str(exc_info.value)


class TestMissingFirstNameException:
    """Test cases for MissingFirstNameException."""

    def test_Initialize_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message."""
        exception = MissingFirstNameException()

        expected_message = "First name is required but was not provided."
        assert str(exception) == expected_message
        assert exception.code == 400

    def test_RaiseException_ShouldBeRaisable(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(MissingFirstNameException) as exc_info:
            raise MissingFirstNameException()

        assert "First name is required but was not provided." in str(exc_info.value)


class TestMissingLastNameException:
    """Test cases for MissingLastNameException."""

    def test_Initialize_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message."""
        exception = MissingLastNameException()

        expected_message = "Last name is required but was not provided."
        assert str(exception) == expected_message
        assert exception.code == 400

    def test_RaiseException_ShouldBeRaisable(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(MissingLastNameException) as exc_info:
            raise MissingLastNameException()

        assert "Last name is required but was not provided." in str(exc_info.value)


class TestMissingUsernameException:
    """Test cases for MissingUsernameException."""

    def test_Initialize_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message."""
        exception = MissingUsernameException()

        expected_message = "Username is required but was not provided."
        assert str(exception) == expected_message
        assert exception.code == 400

    def test_RaiseException_ShouldBeRaisable(self):
        """Test that exception can be raised and caught."""
        with pytest.raises(MissingUsernameException) as exc_info:
            raise MissingUsernameException()

        assert "Username is required but was not provided." in str(exc_info.value)


class TestMemberNotFoundException:
    """Test cases for MemberNotFoundException."""

    def test_InitializeWithMemberId_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message and member ID."""
        member_id = str(MemberId.Generate())

        exception = MemberNotFoundException(member_id)

        expected_message = f"Member with ID '{member_id}' was not found."
        assert str(exception) == expected_message
        assert exception.code == 400

    def test_InitializeWithStringId_ShouldSetCorrectMessage(self):
        """Test that exception handles string ID correctly."""
        member_id = "550e8400-e29b-41d4-a716-446655440000"

        exception = MemberNotFoundException(member_id)

        expected_message = f"Member with ID '{member_id}' was not found."
        assert str(exception) == expected_message
        assert exception.code == 400

    def test_RaiseException_ShouldBeRaisable(self):
        """Test that exception can be raised and caught with member ID."""
        member_id = str(MemberId.Generate())

        with pytest.raises(MemberNotFoundException) as exc_info:
            raise MemberNotFoundException(member_id)

        assert f"Member with ID '{member_id}' was not found." in str(exc_info.value)


class TestMemberAlreadyExistsException:
    """Test cases for MemberAlreadyExistsException."""

    def test_InitializeWithMemberId_ShouldSetCorrectMessage(self):
        """Test that exception initializes with correct message and member ID."""
        member_id = str(MemberId.Generate())

        exception = MemberAlreadyExistsException(member_id)

        expected_message = f"Member with ID '{member_id}' already exists."
        assert str(exception) == expected_message
        assert exception.code == 400

    def test_InitializeWithStringId_ShouldSetCorrectMessage(self):
        """Test that exception handles string ID correctly."""
        member_id = "550e8400-e29b-41d4-a716-446655440001"

        exception = MemberAlreadyExistsException(member_id)

        expected_message = f"Member with ID '{member_id}' already exists."
        assert str(exception) == expected_message
        assert exception.code == 400

    def test_RaiseException_ShouldBeRaisable(self):
        """Test that exception can be raised and caught with member ID."""
        member_id = str(MemberId.Generate())

        with pytest.raises(MemberAlreadyExistsException) as exc_info:
            raise MemberAlreadyExistsException(member_id)

        assert f"Member with ID '{member_id}' already exists." in str(exc_info.value)
