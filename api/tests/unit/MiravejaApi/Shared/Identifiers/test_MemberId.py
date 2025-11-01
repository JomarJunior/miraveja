from uuid import UUID
import pytest
from unittest.mock import patch, MagicMock

from MiravejaApi.Shared.Identifiers.Models import MemberId, StrId
from MiravejaApi.Shared.Identifiers.Exceptions import InvalidUUIDException


class TestMemberId:
    """Test cases for MemberId identifier model that inherits from StrId."""

    def test_InitializeWithValidUUID_ShouldSetCorrectId(self):
        """Test that MemberId initializes with valid UUID4 string."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        member_id = MemberId(id=valid_uuid)

        assert member_id.id == valid_uuid

    def test_InitializeWithUppercaseUUID_ShouldSetCorrectId(self):
        """Test that MemberId accepts uppercase UUID4 string."""
        valid_uuid = "123E4567-E89B-12D3-A456-426614174000"
        member_id = MemberId(id=valid_uuid)

        assert member_id.id == valid_uuid

    def test_InitializeWithLowercaseUUID_ShouldSetCorrectId(self):
        """Test that MemberId accepts lowercase UUID4 string."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        member_id = MemberId(id=valid_uuid)

        assert member_id.id == valid_uuid

    def test_InitializeWithMixedCaseUUID_ShouldSetCorrectId(self):
        """Test that MemberId accepts mixed case UUID4 string."""
        valid_uuid = "123E4567-e89b-12D3-a456-426614174000"
        member_id = MemberId(id=valid_uuid)

        assert member_id.id == valid_uuid

    def test_InitializeWithInvalidUUIDFormat_ShouldRaiseInvalidUUIDException(self):
        """Test that MemberId raises InvalidUUIDException with invalid UUID format."""
        invalid_uuid = "invalid-member-id"

        with pytest.raises(InvalidUUIDException):
            MemberId(id=invalid_uuid)

    def test_InitializeWithTooShortString_ShouldRaiseInvalidUUIDException(self):
        """Test that MemberId raises InvalidUUIDException with too short string."""
        invalid_uuid = "123e4567-e89b-12d3-a456"

        with pytest.raises(InvalidUUIDException):
            MemberId(id=invalid_uuid)

    def test_InitializeWithTooLongString_ShouldRaiseInvalidUUIDException(self):
        """Test that MemberId raises InvalidUUIDException with too long string."""
        invalid_uuid = "123e4567-e89b-12d3-a456-426614174000-extra"

        with pytest.raises(InvalidUUIDException):
            MemberId(id=invalid_uuid)

    def test_InitializeWithMissingHyphens_ShouldRaiseInvalidUUIDException(self):
        """Test that MemberId raises InvalidUUIDException with missing hyphens."""
        invalid_uuid = "123e4567e89b12d3a456426614174000"

        with pytest.raises(InvalidUUIDException):
            MemberId(id=invalid_uuid)

    def test_InitializeWithExtraHyphens_ShouldRaiseInvalidUUIDException(self):
        """Test that MemberId raises InvalidUUIDException with extra hyphens."""
        invalid_uuid = "123e-4567-e89b-12d3-a456-426614174000"

        with pytest.raises(InvalidUUIDException):
            MemberId(id=invalid_uuid)

    def test_InitializeWithInvalidCharacters_ShouldRaiseInvalidUUIDException(self):
        """Test that MemberId raises InvalidUUIDException with invalid characters."""
        invalid_uuid = "123g4567-e89b-12d3-a456-426614174000"

        with pytest.raises(InvalidUUIDException):
            MemberId(id=invalid_uuid)

    def test_InitializeWithEmptyString_ShouldRaiseInvalidUUIDException(self):
        """Test that MemberId raises InvalidUUIDException with empty string."""
        with pytest.raises(InvalidUUIDException):
            MemberId(id="")

    def test_StrMethodWithValidId_ShouldReturnIdString(self):
        """Test that __str__ method returns the id string."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        member_id = MemberId(id=valid_uuid)

        assert str(member_id) == valid_uuid

    def test_SerializeIdWithValidId_ShouldReturnIdString(self):
        """Test that SerializeId method returns the id string."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        member_id = MemberId(id=valid_uuid)

        assert member_id.SerializeId() == valid_uuid

    @patch("uuid.uuid4")
    def test_GenerateWithMockedUUID_ShouldReturnNewMemberIdWithGeneratedUUID(self, mock_uuid4: MagicMock):
        """Test that Generate creates new MemberId with generated UUID4."""
        mock_uuid = UUID("123e4567-e89b-12d3-a456-426614174000")
        mock_uuid4.return_value = mock_uuid

        member_id = MemberId.Generate()

        assert isinstance(member_id, MemberId)
        assert member_id.id == str(mock_uuid)
        mock_uuid4.assert_called_once()

    def test_GenerateMultipleTimes_ShouldReturnDifferentInstances(self):
        """Test that Generate creates different MemberId instances each time."""
        member_id1 = MemberId.Generate()
        member_id2 = MemberId.Generate()

        assert isinstance(member_id1, MemberId)
        assert isinstance(member_id2, MemberId)
        assert member_id1.id != member_id2.id
        assert member_id1 is not member_id2

    def test_GeneratedIdShouldFollowUUIDPattern(self):
        """Test that Generate creates valid UUID4 formatted IDs."""
        member_id = MemberId.Generate()

        # The generated ID should be valid according to the UUID pattern
        import re

        uuid_pattern = r"^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$"
        assert re.match(uuid_pattern, member_id.id, re.IGNORECASE)

    def test_InheritanceFromStrId_ShouldBeInstanceOfStrId(self):
        """Test that MemberId is an instance of StrId."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        member_id = MemberId(id=valid_uuid)

        assert isinstance(member_id, StrId)
        assert isinstance(member_id, MemberId)

    def test_EqualityWithSameId_ShouldReturnTrue(self):
        """Test that two MemberId instances with same id are equal."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        member_id1 = MemberId(id=valid_uuid)
        member_id2 = MemberId(id=valid_uuid)

        assert member_id1 == member_id2

    def test_EqualityWithDifferentId_ShouldReturnFalse(self):
        """Test that two MemberId instances with different id are not equal."""
        member_id1 = MemberId(id="123e4567-e89b-12d3-a456-426614174000")
        member_id2 = MemberId(id="123e4567-e89b-12d3-a456-426614174001")

        assert member_id1 != member_id2

    def test_EqualityWithStrIdSameId_ShouldReturnTrue(self):
        """Test that MemberId and StrId with same id are equal."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        member_id = MemberId(id=valid_uuid)
        str_id = StrId(id=valid_uuid)

        assert member_id == str_id

    def test_HashWithSameId_ShouldReturnSameHash(self):
        """Test that two MemberId instances with same id have same hash."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        member_id1 = MemberId(id=valid_uuid)
        member_id2 = MemberId(id=valid_uuid)

        assert hash(member_id1) == hash(member_id2)

    def test_HashWithDifferentId_ShouldReturnDifferentHash(self):
        """Test that two MemberId instances with different id have different hash."""
        member_id1 = MemberId(id="123e4567-e89b-12d3-a456-426614174000")
        member_id2 = MemberId(id="123e4567-e89b-12d3-a456-426614174001")

        assert hash(member_id1) != hash(member_id2)
