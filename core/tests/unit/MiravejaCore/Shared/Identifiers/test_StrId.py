from uuid import UUID
import pytest
from unittest.mock import patch, MagicMock

from MiravejaCore.Shared.Identifiers.Models import StrId
from MiravejaCore.Shared.Identifiers.Exceptions import InvalidUUIDException


class TestStrId:
    """Test cases for StrId identifier model."""

    def test_InitializeWithValidUUID_ShouldSetCorrectId(self):
        """Test that StrId initializes with valid UUID4 string."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        str_id = StrId(id=valid_uuid)

        assert str_id.id == valid_uuid

    def test_InitializeWithUppercaseUUID_ShouldSetCorrectId(self):
        """Test that StrId accepts uppercase UUID4 string."""
        valid_uuid = "123E4567-E89B-12D3-A456-426614174000"
        str_id = StrId(id=valid_uuid)

        assert str_id.id == valid_uuid

    def test_InitializeWithLowercaseUUID_ShouldSetCorrectId(self):
        """Test that StrId accepts lowercase UUID4 string."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        str_id = StrId(id=valid_uuid)

        assert str_id.id == valid_uuid

    def test_InitializeWithMixedCaseUUID_ShouldSetCorrectId(self):
        """Test that StrId accepts mixed case UUID4 string."""
        valid_uuid = "123E4567-e89b-12D3-a456-426614174000"
        str_id = StrId(id=valid_uuid)

        assert str_id.id == valid_uuid

    def test_InitializeWithInvalidUUIDFormat_ShouldRaiseInvalidUUIDException(self):
        """Test that StrId raises InvalidUUIDException with invalid UUID format."""
        invalid_uuid = "invalid-uuid-format"

        with pytest.raises(InvalidUUIDException):
            StrId(id=invalid_uuid)

    def test_InitializeWithTooShortString_ShouldRaiseInvalidUUIDException(self):
        """Test that StrId raises InvalidUUIDException with too short string."""
        invalid_uuid = "123e4567-e89b-12d3-a456"

        with pytest.raises(InvalidUUIDException):
            StrId(id=invalid_uuid)

    def test_InitializeWithTooLongString_ShouldRaiseInvalidUUIDException(self):
        """Test that StrId raises InvalidUUIDException with too long string."""
        invalid_uuid = "123e4567-e89b-12d3-a456-426614174000-extra"

        with pytest.raises(InvalidUUIDException):
            StrId(id=invalid_uuid)

    def test_InitializeWithMissingHyphens_ShouldRaiseInvalidUUIDException(self):
        """Test that StrId raises InvalidUUIDException with missing hyphens."""
        invalid_uuid = "123e4567e89b12d3a456426614174000"

        with pytest.raises(InvalidUUIDException):
            StrId(id=invalid_uuid)

    def test_InitializeWithExtraHyphens_ShouldRaiseInvalidUUIDException(self):
        """Test that StrId raises InvalidUUIDException with extra hyphens."""
        invalid_uuid = "123e-4567-e89b-12d3-a456-426614174000"

        with pytest.raises(InvalidUUIDException):
            StrId(id=invalid_uuid)

    def test_InitializeWithInvalidCharacters_ShouldRaiseInvalidUUIDException(self):
        """Test that StrId raises InvalidUUIDException with invalid characters."""
        invalid_uuid = "123g4567-e89b-12d3-a456-426614174000"

        with pytest.raises(InvalidUUIDException):
            StrId(id=invalid_uuid)

    def test_InitializeWithEmptyString_ShouldRaiseInvalidUUIDException(self):
        """Test that StrId raises InvalidUUIDException with empty string."""
        with pytest.raises(InvalidUUIDException):
            StrId(id="")

    def test_StrMethodWithValidId_ShouldReturnIdString(self):
        """Test that __str__ method returns the id string."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        str_id = StrId(id=valid_uuid)

        assert str(str_id) == valid_uuid

    def test_SerializeIdWithValidId_ShouldReturnIdString(self):
        """Test that SerializeId method returns the id string."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        str_id = StrId(id=valid_uuid)

        assert str_id.SerializeId() == valid_uuid

    @patch("uuid.uuid4")
    def test_GenerateWithMockedUUID_ShouldReturnNewStrIdWithGeneratedUUID(self, mock_uuid4: MagicMock):
        """Test that Generate creates new StrId with generated UUID4."""
        mock_uuid = UUID("123e4567-e89b-12d3-a456-426614174000")
        mock_uuid4.return_value = mock_uuid

        str_id = StrId.Generate()

        assert isinstance(str_id, StrId)
        assert str_id.id == str(mock_uuid)
        mock_uuid4.assert_called_once()

    def test_GenerateMultipleTimes_ShouldReturnDifferentInstances(self):
        """Test that Generate creates different StrId instances each time."""
        str_id1 = StrId.Generate()
        str_id2 = StrId.Generate()

        assert isinstance(str_id1, StrId)
        assert isinstance(str_id2, StrId)
        assert str_id1.id != str_id2.id
        assert str_id1 is not str_id2

    def test_GeneratedIdShouldFollowUUIDPattern(self):
        """Test that Generate creates valid UUID4 formatted IDs."""
        str_id = StrId.Generate()

        # The generated ID should be valid according to the UUID pattern
        import re

        uuid_pattern = r"^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$"
        assert re.match(uuid_pattern, str_id.id, re.IGNORECASE)

    def test_EqualityWithSameId_ShouldReturnTrue(self):
        """Test that two StrId instances with same id are equal."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        str_id1 = StrId(id=valid_uuid)
        str_id2 = StrId(id=valid_uuid)

        assert str_id1 == str_id2

    def test_EqualityWithDifferentId_ShouldReturnFalse(self):
        """Test that two StrId instances with different id are not equal."""
        str_id1 = StrId(id="123e4567-e89b-12d3-a456-426614174000")
        str_id2 = StrId(id="123e4567-e89b-12d3-a456-426614174001")

        assert str_id1 != str_id2

    def test_HashWithSameId_ShouldReturnSameHash(self):
        """Test that two StrId instances with same id have same hash."""
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        str_id1 = StrId(id=valid_uuid)
        str_id2 = StrId(id=valid_uuid)

        assert hash(str_id1) == hash(str_id2)

    def test_HashWithDifferentId_ShouldReturnDifferentHash(self):
        """Test that two StrId instances with different id have different hash."""
        str_id1 = StrId(id="123e4567-e89b-12d3-a456-426614174000")
        str_id2 = StrId(id="123e4567-e89b-12d3-a456-426614174001")

        assert hash(str_id1) != hash(str_id2)
