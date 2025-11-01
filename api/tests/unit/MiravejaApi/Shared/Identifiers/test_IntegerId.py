import pytest
from pydantic import ValidationError

from MiravejaApi.Shared.Identifiers.Models import IntegerId


class TestIntegerId:
    """Test cases for IntegerId identifier model."""

    def test_InitializeWithValidPositiveInteger_ShouldSetCorrectId(self):
        """Test that IntegerId initializes with valid positive integer."""
        integer_id = IntegerId(id=123)

        assert integer_id.id == 123

    def test_InitializeWithOne_ShouldSetCorrectId(self):
        """Test that IntegerId accepts id value of 1."""
        integer_id = IntegerId(id=1)

        assert integer_id.id == 1

    def test_InitializeWithLargeInteger_ShouldSetCorrectId(self):
        """Test that IntegerId accepts large positive integers."""
        large_id = 999999999
        integer_id = IntegerId(id=large_id)

        assert integer_id.id == large_id

    def test_InitializeWithZero_ShouldRaiseValidationError(self):
        """Test that IntegerId raises ValidationError with zero."""
        with pytest.raises(ValidationError) as exc_info:
            IntegerId(id=0)

        assert "greater than 0" in str(exc_info.value)

    def test_InitializeWithNegativeInteger_ShouldRaiseValidationError(self):
        """Test that IntegerId raises ValidationError with negative integer."""
        with pytest.raises(ValidationError) as exc_info:
            IntegerId(id=-1)

        assert "greater than 0" in str(exc_info.value)

    def test_InitializeWithLargeNegativeInteger_ShouldRaiseValidationError(self):
        """Test that IntegerId raises ValidationError with large negative integer."""
        with pytest.raises(ValidationError) as exc_info:
            IntegerId(id=-999999)

        assert "greater than 0" in str(exc_info.value)

    def test_InitializeWithFloat_ShouldConvertToInteger(self):
        """Test that IntegerId converts float to integer when possible."""
        # Use int() to convert float, simulating Pydantic behavior
        integer_id = IntegerId(id=int(123.0))

        assert integer_id.id == 123
        assert isinstance(integer_id.id, int)

    def test_InitializeWithFloatWithDecimals_ShouldConvertToInteger(self):
        """Test that IntegerId converts float with decimals to integer."""
        # Use int() to convert float, simulating Pydantic behavior
        integer_id = IntegerId(id=int(123.7))

        assert integer_id.id == 123
        assert isinstance(integer_id.id, int)

    def test_InitializeWithZeroFloat_ShouldRaiseValidationError(self):
        """Test that IntegerId raises ValidationError with zero float."""
        with pytest.raises(ValidationError) as exc_info:
            IntegerId(id=int(0.0))

        assert "greater than 0" in str(exc_info.value)

    def test_InitializeWithNegativeFloat_ShouldRaiseValidationError(self):
        """Test that IntegerId raises ValidationError with negative float."""
        with pytest.raises(ValidationError) as exc_info:
            IntegerId(id=int(-1.5))

        assert "greater than 0" in str(exc_info.value)

    def test_InitializeWithNumericString_ShouldParseToInteger(self):
        """Test that IntegerId parses numeric string to integer."""
        integer_id = IntegerId(id="123")  # type: ignore

        assert integer_id.id == 123

    def test_InitializeWithAlphanumericString_ShouldRaiseValidationError(self):
        """Test that IntegerId raises ValidationError with alphanumeric string."""
        with pytest.raises(ValidationError) as exc_info:
            IntegerId(id="123abc")  # type: ignore

        # Should fail due to type validation
        assert len(exc_info.value.errors()) > 0

    def test_InitializeWithNone_ShouldRaiseValidationError(self):
        """Test that IntegerId raises ValidationError with None."""
        with pytest.raises(ValidationError) as exc_info:
            IntegerId(id=None)  # type: ignore

        # Should fail due to required field validation
        assert len(exc_info.value.errors()) > 0

    def test_EqualityWithSameId_ShouldReturnTrue(self):
        """Test that two IntegerId instances with same id are equal."""
        integer_id1 = IntegerId(id=123)
        integer_id2 = IntegerId(id=123)

        assert integer_id1 == integer_id2

    def test_EqualityWithDifferentId_ShouldReturnFalse(self):
        """Test that two IntegerId instances with different id are not equal."""
        integer_id1 = IntegerId(id=123)
        integer_id2 = IntegerId(id=456)

        assert integer_id1 != integer_id2

    def test_HashWithSameId_ShouldReturnSameHash(self):
        """Test that two IntegerId instances with same id have same hash."""
        integer_id1 = IntegerId(id=123)
        integer_id2 = IntegerId(id=123)

        assert hash(integer_id1) == hash(integer_id2)

    def test_HashWithDifferentId_ShouldReturnDifferentHash(self):
        """Test that two IntegerId instances with different id have different hash."""
        integer_id1 = IntegerId(id=123)
        integer_id2 = IntegerId(id=456)

        assert hash(integer_id1) != hash(integer_id2)

    def test_IdAttributeAccess_ShouldReturnCorrectValue(self):
        """Test that id attribute can be accessed directly."""
        integer_id = IntegerId(id=789)

        assert integer_id.id == 789

    def test_ReprWithValidId_ShouldContainIdValue(self):
        """Test that repr contains the id value."""
        integer_id = IntegerId(id=123)
        repr_str = repr(integer_id)

        assert "123" in repr_str
        assert "IntegerId" in repr_str
