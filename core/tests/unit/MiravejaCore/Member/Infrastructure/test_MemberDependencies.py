"""Unit tests for MemberDependencies module."""

from unittest.mock import MagicMock

import pytest

from MiravejaCore.Member.Application.FindMemberById import FindMemberByIdHandler
from MiravejaCore.Member.Application.ListAllMembers import ListAllMembersHandler
from MiravejaCore.Member.Application.RegisterMember import RegisterMemberHandler
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Member.Infrastructure.MemberDependencies import MemberDependencies
from MiravejaCore.Member.Infrastructure.Sql.Repositories import SqlMemberRepository
from MiravejaCore.Shared.DatabaseManager.Infrastructure.Factories import SqlDatabaseManagerFactory
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class TestMemberDependencies:
    """Test cases for MemberDependencies configuration."""

    def test_RegisterDependencies_ShouldRegisterMemberRepository(self):
        """Test that RegisterDependencies registers IMemberRepository."""
        container = Container()

        # Register dependencies
        MemberDependencies.RegisterDependencies(container)

        # Verify IMemberRepository is registered
        repository = container.Get(IMemberRepository.__name__)
        assert repository is not None
        assert repository == SqlMemberRepository

    def test_RegisterDependencies_ShouldRegisterListAllMembersHandler(self):
        """Test that RegisterDependencies registers ListAllMembersHandler with dependencies."""
        container = Container()

        # Setup mock dependencies
        mock_db_factory = MagicMock(spec=SqlDatabaseManagerFactory)
        mock_logger = MagicMock(spec=ILogger)
        mock_event_dispatcher = MagicMock(spec=EventDispatcher)
        container.instances[SqlDatabaseManagerFactory.__name__] = mock_db_factory
        container.instances[ILogger.__name__] = mock_logger
        container.instances[EventDispatcher.__name__] = mock_event_dispatcher

        # Register dependencies
        MemberDependencies.RegisterDependencies(container)

        # Verify handler is registered and created with correct dependencies
        handler = container.Get(ListAllMembersHandler.__name__)
        assert handler is not None
        assert isinstance(handler, ListAllMembersHandler)
        assert handler._databaseManagerFactory == mock_db_factory
        assert handler._logger == mock_logger
        assert handler._eventDispatcher == mock_event_dispatcher

    def test_RegisterDependencies_ShouldRegisterFindMemberByIdHandler(self):
        """Test that RegisterDependencies registers FindMemberByIdHandler."""
        container = Container()

        # Setup mock dependencies
        mock_db_factory = MagicMock(spec=SqlDatabaseManagerFactory)
        mock_logger = MagicMock(spec=ILogger)
        container.instances[SqlDatabaseManagerFactory.__name__] = mock_db_factory
        container.instances[ILogger.__name__] = mock_logger

        # Register dependencies
        MemberDependencies.RegisterDependencies(container)

        # Verify handler is registered
        handler = container.Get(FindMemberByIdHandler.__name__)
        assert handler is not None
        assert isinstance(handler, FindMemberByIdHandler)
        assert handler._databaseManagerFactory == mock_db_factory
        assert handler._logger == mock_logger

    def test_RegisterDependencies_ShouldRegisterRegisterMemberHandler(self):
        """Test that RegisterDependencies registers RegisterMemberHandler."""
        container = Container()

        # Setup mock dependencies
        mock_db_factory = MagicMock(spec=SqlDatabaseManagerFactory)
        mock_logger = MagicMock(spec=ILogger)
        mock_event_dispatcher = MagicMock(spec=EventDispatcher)
        container.instances[SqlDatabaseManagerFactory.__name__] = mock_db_factory
        container.instances[ILogger.__name__] = mock_logger
        container.instances[EventDispatcher.__name__] = mock_event_dispatcher

        # Register dependencies
        MemberDependencies.RegisterDependencies(container)

        # Verify handler is registered with all dependencies
        handler = container.Get(RegisterMemberHandler.__name__)
        assert handler is not None
        assert isinstance(handler, RegisterMemberHandler)
        assert handler._databaseManagerFactory == mock_db_factory
        assert handler._logger == mock_logger
        assert handler._eventDispatcher == mock_event_dispatcher

    def test_RegisterDependencies_AllHandlers_ShouldBeRegisteredAsFactories(self):
        """Test that all handlers are registered as factories (create new instance each time)."""
        container = Container()

        # Setup mock dependencies
        container.instances[SqlDatabaseManagerFactory.__name__] = MagicMock()
        container.instances[ILogger.__name__] = MagicMock()
        container.instances[EventDispatcher.__name__] = MagicMock()

        # Register dependencies
        MemberDependencies.RegisterDependencies(container)

        # Get multiple instances
        handler1 = container.Get(ListAllMembersHandler.__name__)
        handler2 = container.Get(ListAllMembersHandler.__name__)

        # Verify they are different instances (factory pattern)
        assert handler1 is not handler2

    def test_RegisterDependencies_ShouldInjectCorrectRepositoryType(self):
        """Test that handlers receive SqlMemberRepository as repository implementation."""
        container = Container()

        # Setup mock dependencies
        container.instances[SqlDatabaseManagerFactory.__name__] = MagicMock()
        container.instances[ILogger.__name__] = MagicMock()
        container.instances[EventDispatcher.__name__] = MagicMock()

        # Register dependencies
        MemberDependencies.RegisterDependencies(container)

        # Get handler and verify it has the SQL repository type
        handler = container.Get(FindMemberByIdHandler.__name__)
        assert handler._tMemberRepository == SqlMemberRepository

    def test_RegisterDependencies_AllHandlers_ShouldBeAccessible(self):
        """Test that all three handlers can be retrieved from container."""
        container = Container()

        # Setup mock dependencies
        container.instances[SqlDatabaseManagerFactory.__name__] = MagicMock()
        container.instances[ILogger.__name__] = MagicMock()
        container.instances[EventDispatcher.__name__] = MagicMock()

        # Register dependencies
        MemberDependencies.RegisterDependencies(container)

        # Verify all handlers can be retrieved
        list_handler = container.Get(ListAllMembersHandler.__name__)
        find_handler = container.Get(FindMemberByIdHandler.__name__)
        register_handler = container.Get(RegisterMemberHandler.__name__)

        assert list_handler is not None
        assert find_handler is not None
        assert register_handler is not None
