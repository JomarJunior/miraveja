import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from MiravejaApi.Member.Domain.Models import Member
from MiravejaApi.Shared.Identifiers.Exceptions import InvalidUUIDException
from MiravejaApi.Shared.Identifiers.Models import MemberId
from MiravejaApi.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaApi.Member.Domain.Exceptions import (
    MissingEmailException,
    MissingFirstNameException,
    MissingLastNameException,
)


class TestMember:
    """Test cases for Member domain model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that Member initializes with valid data."""
        member_id = MemberId.Generate()
        email = "test@example.com"
        first_name = "John"
        last_name = "Doe"

        member = Member(id=member_id, email=email, firstName=first_name, lastName=last_name)

        assert member.id == member_id
        assert member.email == email
        assert member.firstName == first_name
        assert member.lastName == last_name
        assert isinstance(member.registeredAt, datetime)
        assert isinstance(member.updatedAt, datetime)
        assert member.registeredAt.tzinfo == timezone.utc
        assert member.updatedAt.tzinfo == timezone.utc

    def test_InitializeWithCustomTimestamps_ShouldSetCorrectValues(self):
        """Test that Member accepts custom timestamps."""
        member_id = MemberId.Generate()
        registered_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        updated_at = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

        member = Member(
            id=member_id,
            email="test@example.com",
            firstName="John",
            lastName="Doe",
            registeredAt=registered_at,
            updatedAt=updated_at,
        )

        assert member.registeredAt == registered_at
        assert member.updatedAt == updated_at

    def test_InitializeWithEmptyFirstName_ShouldRaiseValidationError(self):
        """Test that Member raises validation error with empty first name."""
        member_id = MemberId.Generate()

        with pytest.raises(ValidationError) as exc_info:
            Member(id=member_id, email="test@example.com", firstName="", lastName="Doe")

        assert "at least 1 character" in str(exc_info.value)

    def test_InitializeWithTooLongFirstName_ShouldRaiseValidationError(self):
        """Test that Member raises validation error with first name too long."""
        member_id = MemberId.Generate()
        long_name = "a" * 51  # Exceeds 50 character limit

        with pytest.raises(ValidationError) as exc_info:
            Member(id=member_id, email="test@example.com", firstName=long_name, lastName="Doe")

        assert "at most 50 character" in str(exc_info.value)

    def test_InitializeWithEmptyLastName_ShouldRaiseValidationError(self):
        """Test that Member raises validation error with empty last name."""
        member_id = MemberId.Generate()

        with pytest.raises(ValidationError) as exc_info:
            Member(id=member_id, email="test@example.com", firstName="John", lastName="")

        assert "at least 1 character" in str(exc_info.value)

    def test_InitializeWithTooLongLastName_ShouldRaiseValidationError(self):
        """Test that Member raises validation error with last name too long."""
        member_id = MemberId.Generate()
        long_name = "a" * 51  # Exceeds 50 character limit

        with pytest.raises(ValidationError) as exc_info:
            Member(id=member_id, email="test@example.com", firstName="John", lastName=long_name)

        assert "at most 50 character" in str(exc_info.value)

    def test_InitializeWithInvalidEmail_ShouldRaiseValidationError(self):
        """Test that Member raises validation error with invalid email."""
        member_id = MemberId.Generate()

        with pytest.raises(ValidationError) as exc_info:
            Member(id=member_id, email="invalid-email", firstName="John", lastName="Doe")

        # Should contain email validation error
        assert "value is not a valid email address" in str(exc_info.value)
        assert "invalid-email" in str(exc_info.value)

    def test_RegisterWithValidData_ShouldCreateMemberWithDefaults(self):
        """Test that Register creates Member with valid data and default timestamps."""
        member_id = MemberId.Generate()
        email = "test@example.com"
        first_name = "John"
        last_name = "Doe"

        member = Member.Register(member_id, email, first_name, last_name)

        assert member.id == member_id
        assert member.email == email
        assert member.firstName == first_name
        assert member.lastName == last_name
        assert isinstance(member.registeredAt, datetime)
        assert isinstance(member.updatedAt, datetime)

    def test_CreateFromKeycloakUserWithValidData_ShouldCreateMember(self):
        """Test that CreateFromKeycloakUser creates Member from valid KeycloakUser."""
        keycloak_user = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="testuser",
            email="test@example.com",
            firstName="John",
            lastName="Doe",
            emailVerified=True,
        )

        member = Member.CreateFromKeycloakUser(keycloak_user)

        assert member.id.id == keycloak_user.id
        assert member.email == keycloak_user.email
        assert member.firstName == keycloak_user.firstName
        assert member.lastName == keycloak_user.lastName

    def test_CreateFromKeycloakUserWithNoEmail_ShouldRaiseMissingEmailException(self):
        """Test that CreateFromKeycloakUser raises exception when email is missing."""
        keycloak_user = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="testuser",
            email=None,
            firstName="John",
            lastName="Doe",
            emailVerified=False,
        )

        with pytest.raises(MissingEmailException):
            Member.CreateFromKeycloakUser(keycloak_user)

    def test_CreateFromKeycloakUserWithNoFirstName_ShouldRaiseMissingFirstNameException(self):
        """Test that CreateFromKeycloakUser raises exception when first name is missing."""
        keycloak_user = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="testuser",
            email="test@example.com",
            firstName=None,
            lastName="Doe",
            emailVerified=True,
        )

        with pytest.raises(MissingFirstNameException):
            Member.CreateFromKeycloakUser(keycloak_user)

    def test_CreateFromKeycloakUserWithNoLastName_ShouldRaiseMissingLastNameException(self):
        """Test that CreateFromKeycloakUser raises exception when last name is missing."""
        keycloak_user = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="testuser",
            email="test@example.com",
            firstName="John",
            lastName=None,
            emailVerified=True,
        )

        with pytest.raises(MissingLastNameException):
            Member.CreateFromKeycloakUser(keycloak_user)

    def test_CreateFromKeycloakUserWithInvalidEmail_ShouldRaiseValidationError(self):
        """Test that CreateFromKeycloakUser raises exception when email is invalid."""
        keycloak_user = KeycloakUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            username="testuser",
            email="invalid-email",
            firstName="John",
            lastName="Doe",
            emailVerified=False,
        )

        with pytest.raises(ValidationError):
            Member.CreateFromKeycloakUser(keycloak_user)

    def test_FromDatabaseWithValidData_ShouldCreateMemberFromDbFields(self):
        """Test that FromDatabase creates Member from database fields."""
        id_str = "123e4567-e89b-12d3-a456-426614174000"
        email = "test@example.com"
        first_name = "John"
        last_name = "Doe"
        registered_at = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        updated_at = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

        member = Member.FromDatabase(
            id=id_str,
            email=email,
            firstName=first_name,
            lastName=last_name,
            registeredAt=registered_at,
            updatedAt=updated_at,
        )

        assert member.id.id == id_str
        assert member.email == email
        assert member.firstName == first_name
        assert member.lastName == last_name
        assert member.registeredAt == registered_at
        assert member.updatedAt == updated_at

    def test_FromDatabaseWithInvalidId_ShouldRaiseValidationError(self):
        """Test that FromDatabase raises validation error with invalid UUID."""
        with pytest.raises(InvalidUUIDException):
            Member.FromDatabase(
                id="invalid-uuid",
                email="test@example.com",
                firstName="John",
                lastName="Doe",
                registeredAt=datetime.now(timezone.utc),
                updatedAt=datetime.now(timezone.utc),
            )

    def test_EqualityWithSameMember_ShouldReturnTrue(self):
        """Test that two Member instances with same data are equal."""
        member_id = MemberId.Generate()
        email = "test@example.com"
        first_name = "John"
        last_name = "Doe"
        timestamp = datetime.now(timezone.utc)

        member1 = Member(
            id=member_id,
            email=email,
            firstName=first_name,
            lastName=last_name,
            registeredAt=timestamp,
            updatedAt=timestamp,
        )

        member2 = Member(
            id=member_id,
            email=email,
            firstName=first_name,
            lastName=last_name,
            registeredAt=timestamp,
            updatedAt=timestamp,
        )

        assert member1 == member2

    def test_EqualityWithDifferentMember_ShouldReturnFalse(self):
        """Test that two Member instances with different data are not equal."""
        member1 = Member(id=MemberId.Generate(), email="test1@example.com", firstName="John", lastName="Doe")

        member2 = Member(id=MemberId.Generate(), email="test2@example.com", firstName="Jane", lastName="Smith")

        assert member1 != member2
