# PyTest Testing Standards and Conventions

This document establishes the testing standards, patterns, and conventions for the MiraVeja API project. All future testing efforts must follow these guidelines to maintain consistency, quality, and maintainability.

## Overview

The MiraVeja API testing strategy follows Domain-Driven Design principles with comprehensive unit testing for all model classes. Tests are organized to mirror the source code structure and provide complete coverage of both success and failure scenarios.

## Project Structure and Organization

### Directory Structure

Tests mirror the source code structure exactly:

```bash
tests/
└── unit/
    └── Miraveja/
        ├── Configuration/
        │   ├── test_AppConfig.py
        │   ├── test_DatabaseConfig.py
        │   ├── test_KeycloakConfigFactory.py
        │   └── test_LoggerConfig.py
        ├── Member/
        │   └── Domain/
        │       └── test_Member.py
        └── Shared/
            ├── DI/
            │   └── test_Container.py
            ├── Errors/
            │   ├── test_DomainException.py
            │   └── test_InfrastructureException.py
            ├── Identifiers/
            │   ├── test_IntegerId.py
            │   ├── test_MemberId.py
            │   └── test_StrId.py
            ├── Logging/
            │   └── test_Logger.py
            └── DatabaseManager/
                └── Infrastructure/
                    └── Sql/
                        └── test_SqlDatabaseManager.py
```

### File Naming Conventions

- **Test Files**: `test_{ClassName}.py` (e.g., `test_AppConfig.py`)
- **Multiple Classes**: Extract each class into separate test files when source file contains multiple definitions
- **Test Classes**: `Test{ClassName}` (e.g., `TestAppConfig`)
- **Test Methods**: `test_{Action}_{Condition}_Should{ExpectedResult}` using PascalCase per project standards

## Code Structure and Patterns

### Test Class Template

```python
import pytest
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

from Miraveja.Path.To.Models import ClassName
from Miraveja.Path.To.Exceptions import CustomException


class TestClassName:
    """Test cases for ClassName model."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that ClassName initializes with valid data."""
        # Arrange
        # Act  
        # Assert

    def test_InitializeWithInvalidData_ShouldRaiseValidationError(self):
        """Test that ClassName raises validation error with invalid data."""
        with pytest.raises(ValidationError) as exc_info:
            # Act that should raise error
            pass
        
        # Verify error details
        assert "expected error message" in str(exc_info.value)
```

### Import Standards

```python
# Standard library imports first
import os
import pytest
from datetime import datetime, timezone
from typing import Dict, Any
from unittest.mock import patch, MagicMock

# Pydantic imports
from pydantic import ValidationError

# Project imports - specific and explicit
from Miraveja.Configuration.Models import LoggerConfig
from Miraveja.Shared.Logging.Enums import LoggerLevel, LoggerTarget
from Miraveja.Shared.Identifiers.Exceptions import InvalidUUIDException
```

## Test Method Naming Conventions

### Established Pattern

**Format**: `test_{Action}_{Condition}_Should{ExpectedResult}`

**Examples**:

- `test_InitializeWithValidData_ShouldSetCorrectValues`
- `test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues`
- `test_ValidateFilenameWithFileTargetAndValidPath_ShouldCreateDirectoryAndReturnPath`
- `test_InitializeWithInvalidEmail_ShouldRaiseValidationError`

### Naming Components

- **Action**: What method/functionality is being tested (`Initialize`, `FromEnv`, `Validate`, `Generate`)
- **Condition**: The specific scenario or input condition (`WithValidData`, `WithInvalidEmail`, `WithNoHandlers`)
- **Expected Result**: What should happen (`ShouldSetCorrectValues`, `ShouldRaiseValidationError`, `ShouldReturnNewInstance`)

## Testing Categories and Coverage Requirements

### 1. Initialization Tests

**Purpose**: Verify object creation with various input scenarios

```python
def test_InitializeWithDefaultValues_ShouldSetCorrectDefaults(self):
    """Test that Model initializes with correct default values."""

def test_InitializeWithCustomValues_ShouldSetCorrectValues(self):
    """Test that Model initializes with custom values correctly."""

def test_InitializeWithInvalidData_ShouldRaiseValidationError(self):
    """Test that Model raises validation error with invalid data."""
```

### 2. Factory Method Tests

**Purpose**: Test static/class methods that create instances

```python
@patch.dict(os.environ, {"KEY": "value"})
def test_FromEnvWithAllEnvironmentVariables_ShouldSetCorrectValues(self):
    """Test that factory method creates instance from environment variables."""

def test_GenerateWithMockedDependency_ShouldReturnNewInstance(self):
    """Test that Generate method creates new instance with mocked dependencies."""
```

### 3. Validation Tests

**Purpose**: Comprehensive validation of business rules and constraints

```python
def test_ValidateFieldWithValidInput_ShouldAcceptValue(self):
    """Test that validation accepts valid input."""

def test_ValidateFieldWithInvalidInput_ShouldRaiseValidationError(self):
    """Test that validation rejects invalid input with appropriate error."""
```

### 4. Behavior Tests

**Purpose**: Test specific behaviors and side effects

```python
@patch('os.makedirs')
def test_ValidateFilenameWithFileTarget_ShouldCreateDirectory(self, mock_makedirs):
    """Test that filename validation creates necessary directories."""
```

## Exception Handling Patterns

### Pydantic ValidationError

```python
def test_InitializeWithInvalidData_ShouldRaiseValidationError(self):
    """Test that initialization raises validation error with invalid data."""
    with pytest.raises(ValidationError) as exc_info:
        Model(invalid_field="invalid_value")
    
    assert "expected error substring" in str(exc_info.value)
```

### Custom Domain/Infrastructure/Application Exceptions

```python
def test_ActionWithInvalidState_ShouldRaiseCustomException(self):
    """Test that action raises custom exception in invalid state."""
    with pytest.raises(CustomDomainException) as exc_info:
        model.perform_action()
    
    assert exc_info.value.message == "Expected error message"
```

## Mocking Strategies

### Environment Variables

```python
@patch.dict(os.environ, {"KEY": "value"}, clear=True)
def test_FromEnvWithSpecificVariables_ShouldUseEnvironmentValues(self):
    """Test environment variable usage."""

@patch.dict(os.environ, {}, clear=True)
def test_FromEnvWithNoVariables_ShouldUseDefaults(self):
    """Test default behavior when environment variables are not set."""
```

### External Dependencies

```python
@patch('os.makedirs')
def test_MethodWithFileSystemOperation_ShouldCallMakedirs(self, mock_makedirs):
    """Test that method calls external file system operations."""
    # Test logic
    mock_makedirs.assert_called_once_with("/expected/path", exist_ok=True)

@patch('logging.getLogger')
def test_LoggerInitialization_ShouldConfigureLogger(self, mock_get_logger):
    """Test logger configuration with mocked logging."""
    mock_python_logger = MagicMock()
    mock_get_logger.return_value = mock_python_logger
    # Test logic
```

### UUID Generation

```python
@patch('uuid.uuid4')
def test_GenerateWithMockedUUID_ShouldReturnExpectedId(self, mock_uuid4):
    """Test ID generation with mocked UUID."""
    expected_uuid = "123e4567-e89b-12d3-a456-426614174000"
    mock_uuid4.return_value.__str__ = lambda: expected_uuid
    
    result = Model.Generate()
    
    assert result.id == expected_uuid
```

## Test Data Management

### Valid Test Data

```python
class TestData:
    """Centralized test data for consistent testing."""
    VALID_UUID = "123e4567-e89b-12d3-a456-426614174000"
    VALID_EMAIL = "test@example.com"
    VALID_NAME = "John Doe"
    
    @staticmethod
    def create_valid_member_data():
        return {
            "id": MemberId.Generate(),
            "email": TestData.VALID_EMAIL,
            "firstName": "John",
            "lastName": "Doe"
        }
```

### Edge Cases and Invalid Data

Always test boundary conditions:

- Empty strings (`""`)
- None values
- Maximum length values
- Minimum length values
- Invalid formats
- Type mismatches

## Documentation Standards

### Test Method Docstrings

Each test method must have a descriptive docstring explaining:

```python
def test_MethodName_Condition_ShouldExpectation(self):
    """Test that [Class/Method] [specific behavior] when [condition]."""
```

### Class Docstrings

```python
class TestClassName:
    """Test cases for ClassName [domain/model/service] [purpose]."""
```

### Inline Comments

Use comments sparingly, only for complex test logic:

```python
# Arrange - complex setup
# Act - the action being tested  
# Assert - verification with explanation if complex
```

## Assertion Patterns

### Basic Assertions

```python
assert result == expected
assert isinstance(result, ExpectedType)
assert result.field == expected_value
assert len(result.collection) == expected_count
```

### Exception Assertions

```python
with pytest.raises(ExceptionType) as exc_info:
    # Action that should raise exception
    
assert "expected message" in str(exc_info.value)
assert exc_info.value.code == expected_code
```

### Mock Assertions

```python
mock_method.assert_called_once()
mock_method.assert_called_once_with(expected_args)
mock_method.assert_not_called()
assert mock_method.call_count == expected_count
```

## Configuration and Dependencies

### pytest Configuration

Tests follow `pyproject.toml` configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src/Miraveja",
    "--cov-report=html",
    "--cov-report=term-missing:skip-covered",
    "--cov-fail-under=80"
]
```

### Required Dependencies

```python
# Core testing
pytest
pytest-cov
pytest-mock

# Mocking and fixtures
unittest.mock (built-in)

# Type checking support
pydantic
typing
```

## Code Quality Standards

### Coverage Requirements

- **Target Coverage**: 80% minimum per `pyproject.toml`
- **Core Models**: Aim for 100% coverage
- **Application Services**: Minimum 90% coverage
- **Infrastructure**: Minimum 75% coverage

### Naming Compliance

All test code follows project `pylint` rules:

- Functions and methods: `PascalCase`
- Variables: `camelCase`
- Constants: `UPPER_CASE`
- File names (specific for testing): `test_PascalCase.py`

### Type Hints

Use type hints for complex test fixtures and helper methods:

```python
def CreateTestMember(email: str = "test@example.com") -> Member:
    """Create a test member instance with specified email."""
    return Member(
        id=MemberId.Generate(),
        email=email,
        firstName="Test",
        lastName="User"
    )
```

## Anti-Patterns to Avoid

### ❌ Don't Do

```python
# Vague test names
def test_member():
def test_validation():

# Missing docstrings
def test_something(self):

# Non-descriptive assertions
assert result
assert not result

# Testing multiple concerns in one test
def test_everything(self):
    # Tests initialization, validation, and business logic

# Hard-coded values without meaning
assert result.count == 5  # Why 5?
```

### ✅ Do This Instead

```python
# Descriptive test names
def test_InitializeWithValidEmail_ShouldSetEmailField(self):
def test_ValidateEmailFormat_ShouldRejectInvalidFormat(self):

# Clear docstrings
def test_FromEnvWithMissingVariables_ShouldUseDefaults(self):
    """Test that FromEnv uses default values when environment variables are missing."""

# Meaningful assertions
assert member.email == expected_email
assert validation_errors is not None

# Single concern per test
def test_InitializeWithValidData_ShouldSetCorrectFields(self):
    # Only tests initialization

# Named constants
EXPECTED_DEFAULT_COUNT = 0
assert result.count == EXPECTED_DEFAULT_COUNT
```

## Future Extensions

### Integration Testing

When adding integration tests:

- Use separate `tests/integration/` directory
- Follow same naming conventions
- Focus on component interactions
- Use test databases and external service mocks

### Performance Testing

For performance-critical code:

- Use `pytest-benchmark` for timing tests
- Create separate `tests/performance/` directory
- Establish baseline performance metrics

### Property-Based Testing

For complex validation logic:

- Use `hypothesis` library
- Generate test data automatically
- Focus on edge cases and invariants

## Conclusion

These standards ensure:

1. **Consistency**: All tests follow the same patterns and conventions
2. **Maintainability**: Clear naming and structure make tests easy to understand and modify
3. **Reliability**: Comprehensive coverage and proper mocking ensure test accuracy
4. **Quality**: High standards for documentation and code quality
5. **Scalability**: Patterns that work for both small and large test suites

All future testing efforts must adhere to these standards. Any deviations should be documented and approved through the standard code review process.
