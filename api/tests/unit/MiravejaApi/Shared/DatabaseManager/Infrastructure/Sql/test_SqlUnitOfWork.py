import pytest
from unittest.mock import MagicMock, Mock
from typing import Type, Any

from MiravejaApi.Shared.databaseManager.Infrastructure.Sql.Models import SqlDatabaseManager
from MiravejaApi.Shared.databaseManager.Domain.Exceptions import SessionNotInitializedError


class MockRepository:
    """Mock repository class for testing."""

    def __init__(self, session):
        self.session = session


class TestSqlDatabaseManager:
    """Test cases for SqlDatabaseManager model."""

    def test_InitializeWithResourceFactory_ShouldSetCorrectDefaults(self):
        """Test that SqlDatabaseManager initializes with resource factory and default values."""
        mock_factory = MagicMock()

        uow = SqlDatabaseManager(mock_factory)

        assert uow._resourceFactory == mock_factory
        assert uow._session is None
        assert len(uow._repositories) == 0

    def test_EnterContextManager_ShouldInitializeSessionAndClearRepositories(self):
        """Test that __enter__ creates session and clears repositories."""
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        uow = SqlDatabaseManager(mock_factory)

        # Pre-populate repositories to test clearing
        uow._repositories[str] = "existing_repo"

        result = uow.__enter__()

        assert result is uow
        assert uow._session == mock_session
        assert len(uow._repositories) == 0
        mock_factory.assert_called_once()

    def test_ExitContextManagerWithoutException_ShouldCloseSession(self):
        """Test that __exit__ closes session when no exception occurs."""
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        uow = SqlDatabaseManager(mock_factory)

        with uow:
            pass  # No exception

        mock_session.close.assert_called_once()

    def test_ExitContextManagerWithException_ShouldRollbackAndCloseSession(self):
        """Test that __exit__ rolls back and closes session when exception occurs."""
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        uow = SqlDatabaseManager(mock_factory)

        try:
            with uow:
                raise ValueError("Test exception")
        except ValueError:
            pass

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_ExitContextManagerWithNoneSession_ShouldNotCallSessionMethods(self):
        """Test that __exit__ handles None session gracefully."""
        mock_factory = MagicMock()
        uow = SqlDatabaseManager(mock_factory)

        # Don't enter context, so session remains None
        result = uow.__exit__(None, None, None)

        assert result is None

    def test_CommitWithActiveSession_ShouldCallSessionCommit(self):
        """Test that Commit calls session commit when session is active."""
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        uow = SqlDatabaseManager(mock_factory)

        with uow:
            uow.Commit()

        mock_session.commit.assert_called_once()

    def test_CommitWithNoneSession_ShouldNotCallCommit(self):
        """Test that Commit handles None session gracefully."""
        mock_factory = MagicMock()
        uow = SqlDatabaseManager(mock_factory)

        # Don't enter context, so session remains None
        uow.Commit()

        # Should not raise exception

    def test_RollbackWithActiveSession_ShouldCallSessionRollback(self):
        """Test that Rollback calls session rollback when session is active."""
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        uow = SqlDatabaseManager(mock_factory)

        with uow:
            uow.Rollback()

        mock_session.rollback.assert_called_once()

    def test_RollbackWithNoneSession_ShouldNotCallRollback(self):
        """Test that Rollback handles None session gracefully."""
        mock_factory = MagicMock()
        uow = SqlDatabaseManager(mock_factory)

        # Don't enter context, so session remains None
        uow.Rollback()

        # Should not raise exception

    def test_GetRepositoryWithActiveSession_ShouldCreateAndCacheRepository(self):
        """Test that GetRepository creates repository with session and caches it."""
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        uow = SqlDatabaseManager(mock_factory)

        with uow:
            repo = uow.GetRepository(MockRepository)

        assert isinstance(repo, MockRepository)
        assert repo.session == mock_session
        assert MockRepository in uow._repositories
        assert uow._repositories[MockRepository] == repo

    def test_GetRepositoryCalledTwice_ShouldReturnCachedRepository(self):
        """Test that GetRepository returns cached repository on subsequent calls."""
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        uow = SqlDatabaseManager(mock_factory)

        with uow:
            repo1 = uow.GetRepository(MockRepository)
            repo2 = uow.GetRepository(MockRepository)

        assert repo1 is repo2
        assert len(uow._repositories) == 1

    def test_GetRepositoryWithNoneSession_ShouldRaiseSessionNotInitializedError(self):
        """Test that GetRepository raises error when session is None."""
        mock_factory = MagicMock()
        uow = SqlDatabaseManager(mock_factory)

        # Don't enter context, so session remains None
        with pytest.raises(SessionNotInitializedError):
            uow.GetRepository(MockRepository)

    def test_GetRepositoryWithDifferentTypes_ShouldCreateSeparateRepositories(self):
        """Test that GetRepository creates separate repositories for different types."""

        class AnotherRepository:
            def __init__(self, session):
                self.session = session

        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        uow = SqlDatabaseManager(mock_factory)

        with uow:
            repo1 = uow.GetRepository(MockRepository)
            repo2 = uow.GetRepository(AnotherRepository)

        assert isinstance(repo1, MockRepository)
        assert isinstance(repo2, AnotherRepository)
        assert repo1 is not repo2
        assert len(uow._repositories) == 2

    def test_ContextManagerProtocol_ShouldWorkWithWithStatement(self):
        """Test that SqlDatabaseManager works correctly with 'with' statement."""
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)

        uow = SqlDatabaseManager(mock_factory)

        # Test successful context
        with uow as context:
            assert context is uow
            assert uow._session == mock_session
            repo = uow.GetRepository(MockRepository)
            assert isinstance(repo, MockRepository)

        mock_session.close.assert_called_once()

    def test_ContextManagerWithExceptionInContext_ShouldHandleGracefully(self):
        """Test that context manager handles exceptions within the context properly."""
        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        uow = SqlDatabaseManager(mock_factory)

        exception_raised = False
        try:
            with uow:
                uow.GetRepository(MockRepository)
                raise RuntimeError("Test error")
        except RuntimeError:
            exception_raised = True

        assert exception_raised
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    def test_ResourceFactoryNotCallable_ShouldStillInitialize(self):
        """Test that SqlDatabaseManager initializes even if resource factory validation is missing."""
        # Note: This tests current behavior - ideally should validate callable
        not_callable = "not_a_function"

        uow = SqlDatabaseManager(not_callable)  # type: ignore

        assert uow._resourceFactory == not_callable

    def test_MultipleRepositoryTypes_ShouldMaintainSeparateInstances(self):
        """Test that multiple repository types are kept separate in cache."""

        class RepoA:
            def __init__(self, session):
                self.session = session
                self.type = "A"

        class RepoB:
            def __init__(self, session):
                self.session = session
                self.type = "B"

        mock_session = MagicMock()
        mock_factory = MagicMock(return_value=mock_session)
        uow = SqlDatabaseManager(mock_factory)

        with uow:
            repo_a1 = uow.GetRepository(RepoA)
            repo_b1 = uow.GetRepository(RepoB)
            repo_a2 = uow.GetRepository(RepoA)
            repo_b2 = uow.GetRepository(RepoB)

        # Same types return same instances
        assert repo_a1 is repo_a2
        assert repo_b1 is repo_b2

        # Different types return different instances
        assert repo_a1 is not repo_b1
        assert len(uow._repositories) == 2
