import pytest

from MiravejaCore.Shared.DI.Exceptions import DependencyNameNotFoundInContainerException


class TestDependencyNameNotFoundInContainerException:
    """Test cases for DependencyNameNotFoundInContainerException domain exception."""

    def test_InitializeWithDependencyName_ShouldSetCorrectMessage(self):
        """Test that DependencyNameNotFoundInContainerException initializes with correct error message."""
        # Arrange
        dependency_name = "TestDependency"
        expected_message = f"Dependency '{dependency_name}' not found in the container."
        expected_code = 500

        # Act
        exception = DependencyNameNotFoundInContainerException(dependency_name)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code

    def test_InitializeWithEmptyDependencyName_ShouldSetCorrectMessage(self):
        """Test that DependencyNameNotFoundInContainerException initializes correctly with empty dependency name."""
        # Arrange
        dependency_name = ""
        expected_message = f"Dependency '{dependency_name}' not found in the container."
        expected_code = 500

        # Act
        exception = DependencyNameNotFoundInContainerException(dependency_name)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code

    def test_InitializeWithSpecialCharactersDependencyName_ShouldSetCorrectMessage(self):
        """Test that DependencyNameNotFoundInContainerException handles special characters in dependency name."""
        # Arrange
        dependency_name = "Dependency@#$%^&*()"
        expected_message = f"Dependency '{dependency_name}' not found in the container."
        expected_code = 500

        # Act
        exception = DependencyNameNotFoundInContainerException(dependency_name)

        # Assert
        assert exception.message == expected_message
        assert exception.code == expected_code
