import pytest

from MiravejaCore.Shared.DatabaseManager.Domain.Exceptions import SessionNotInitializedError


class TestSessionNotInitializedError:
    """Test cases for SessionNotInitializedError domain exception."""

    def test_InitializeWithDefaultValues_ShouldSetCorrectMessage(self):
        """Test that SessionNotInitializedError initializes with correct error message."""
        # Arrange
        expected_message = "Session is not initialized. Ensure you are within a 'with' context."

        # Act
        exception = SessionNotInitializedError()

        # Assert
        assert exception.message == expected_message

    def test_InitializeMultipleTimes_ShouldHaveConsistentMessage(self):
        """Test that SessionNotInitializedError has consistent message across instances."""
        # Arrange
        expected_message = "Session is not initialized. Ensure you are within a 'with' context."

        # Act
        exception1 = SessionNotInitializedError()
        exception2 = SessionNotInitializedError()

        # Assert
        assert exception1.message == expected_message
        assert exception2.message == expected_message
        assert exception1.message == exception2.message
