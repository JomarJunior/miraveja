import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session as DatabaseSession

from MiravejaCore.Shared.DatabaseManager.Infrastructure.Factories import SqlDatabaseManagerFactory
from MiravejaCore.Shared.DatabaseManager.Infrastructure.Sql.Models import SqlDatabaseManager


class TestSqlDatabaseManagerFactory:
    """Test cases for SqlDatabaseManagerFactory."""

    @pytest.fixture
    def mock_resource_factory(self):
        """Create a mock resource factory that returns a mock database session."""
        mock_session = MagicMock(spec=DatabaseSession)
        return lambda: mock_session

    @pytest.fixture
    def factory(self, mock_resource_factory):
        """Create a SqlDatabaseManagerFactory instance with mocked resource factory."""
        return SqlDatabaseManagerFactory(resourceFactory=mock_resource_factory)

    def test_InitializeWithValidResourceFactory_ShouldSetCorrectValues(self, mock_resource_factory):
        """Test that SqlDatabaseManagerFactory initializes with valid resource factory."""
        # Arrange & Act
        factory = SqlDatabaseManagerFactory(resourceFactory=mock_resource_factory)

        # Assert
        assert factory._resourceFactory == mock_resource_factory

    def test_CreateWithValidFactory_ShouldReturnSqlDatabaseManager(self, factory):
        """Test that Create returns SqlDatabaseManager instance."""
        # Act
        result = factory.Create()

        # Assert
        assert result is not None
        assert isinstance(result, SqlDatabaseManager)

    def test_CreateWithValidFactory_ShouldPassResourceFactoryToManager(self, mock_resource_factory):
        """Test that Create passes resource factory to SqlDatabaseManager."""
        # Arrange
        factory = SqlDatabaseManagerFactory(resourceFactory=mock_resource_factory)

        # Act
        result = factory.Create()

        # Assert
        assert result._resourceFactory == mock_resource_factory

    def test_CreateMultipleTimes_ShouldReturnNewInstanceEachTime(self, factory):
        """Test that Create returns new SqlDatabaseManager instance on each call."""
        # Act
        result1 = factory.Create()
        result2 = factory.Create()

        # Assert
        assert result1 is not result2
        assert isinstance(result1, SqlDatabaseManager)
        assert isinstance(result2, SqlDatabaseManager)

    def test_CreateWithCustomResourceFactory_ShouldUseProvidedFactory(self):
        """Test that Create uses the provided resource factory."""
        # Arrange
        customSession = MagicMock(spec=DatabaseSession)
        customResourceFactory = lambda: customSession
        factory = SqlDatabaseManagerFactory(resourceFactory=customResourceFactory)

        # Act
        result = factory.Create()

        # Assert
        assert result._resourceFactory == customResourceFactory
        # Verify the factory can be called and returns the custom session
        assert result._resourceFactory() == customSession
