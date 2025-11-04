import pytest
from unittest.mock import MagicMock

from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.DI.Exceptions import DependencyNameNotFoundInContainerException
from MiravejaCore.Shared.Configuration import AppConfig


class TestContainer:
    """Test cases for Container dependency injection model."""

    def test_InitializeContainer_ShouldCreateEmptyCollections(self):
        """Test that Container initializes with empty collections."""
        container = Container()

        assert len(container.singletons) == 0
        assert len(container.factories) == 0
        assert len(container.instances) == 0

    def test_FromConfigWithValidConfig_ShouldPopulateInstances(self):
        """Test that FromConfig creates container with AppConfig values in instances."""
        app_config = AppConfig(appName="Test App", appVersion="1.0.0")

        container = Container.FromConfig(app_config)

        assert "appName" in container.instances
        assert "appVersion" in container.instances
        assert container.instances["appName"] == "Test App"
        assert container.instances["appVersion"] == "1.0.0"

    def test_RegisterSingletonsWithValidFactories_ShouldUpdateSingletonsDict(self):
        """Test that RegisterSingletons updates the singletons dictionary."""
        container = Container()
        mock_factory = MagicMock()

        singletons = {"service1": mock_factory}
        container.RegisterSingletons(singletons)

        assert "service1" in container.singletons
        assert container.singletons["service1"] == mock_factory

    def test_RegisterSingletonsWithMultipleFactories_ShouldUpdateAllFactories(self):
        """Test that RegisterSingletons updates multiple singleton factories."""
        container = Container()
        mock_factory1 = MagicMock()
        mock_factory2 = MagicMock()

        singletons = {"service1": mock_factory1, "service2": mock_factory2}
        container.RegisterSingletons(singletons)

        assert len(container.singletons) == 2
        assert container.singletons["service1"] == mock_factory1
        assert container.singletons["service2"] == mock_factory2

    def test_RegisterFactoriesWithValidFactories_ShouldUpdateFactoriesDict(self):
        """Test that RegisterFactories updates the factories dictionary."""
        container = Container()
        mock_factory = MagicMock()

        factories = {"service1": mock_factory}
        container.RegisterFactories(factories)

        assert "service1" in container.factories
        assert container.factories["service1"] == mock_factory

    def test_RegisterFactoriesWithMultipleFactories_ShouldUpdateAllFactories(self):
        """Test that RegisterFactories updates multiple factory functions."""
        container = Container()
        mock_factory1 = MagicMock()
        mock_factory2 = MagicMock()

        factories = {"service1": mock_factory1, "service2": mock_factory2}
        container.RegisterFactories(factories)

        assert len(container.factories) == 2
        assert container.factories["service1"] == mock_factory1
        assert container.factories["service2"] == mock_factory2

    def test_GetWithExistingInstance_ShouldReturnCachedInstance(self):
        """Test that Get returns cached instance when available."""
        container = Container()
        test_instance = "cached_value"
        container.instances["service1"] = test_instance

        result = container.Get("service1")

        assert result == test_instance

    def test_GetWithSingletonFactory_ShouldCreateAndCacheInstance(self):
        """Test that Get creates and caches singleton instance."""
        container = Container()
        mock_instance = MagicMock()
        mock_factory = MagicMock(return_value=mock_instance)

        container.RegisterSingletons({"service1": mock_factory})

        result1 = container.Get("service1")
        result2 = container.Get("service1")

        assert result1 == mock_instance
        assert result2 == mock_instance
        assert result1 is result2  # Same instance
        assert "service1" in container.instances
        mock_factory.assert_called_once_with(container)

    def test_GetWithTransientFactory_ShouldCreateNewInstanceEachTime(self):
        """Test that Get creates new instance each time for factories."""
        container = Container()
        mock_instance1 = MagicMock()
        mock_instance2 = MagicMock()
        mock_factory = MagicMock(side_effect=[mock_instance1, mock_instance2])

        container.RegisterFactories({"service1": mock_factory})

        result1 = container.Get("service1")
        result2 = container.Get("service1")

        assert result1 == mock_instance1
        assert result2 == mock_instance2
        assert result1 is not result2  # Different instances
        assert mock_factory.call_count == 2
        mock_factory.assert_any_call(container)

    def test_GetWithNonExistentService_ShouldRaiseDependencyNotFoundException(self):
        """Test that Get raises exception when service is not found."""
        container = Container()

        with pytest.raises(DependencyNameNotFoundInContainerException) as exc_info:
            container.Get("non_existent_service")

        assert "non_existent_service" in str(exc_info.value)

    def test_GetWithInstanceTakesPrecedenceOverSingleton_ShouldReturnInstance(self):
        """Test that Get returns cached instance even when singleton factory exists."""
        container = Container()
        cached_instance = "cached_value"
        mock_factory = MagicMock(return_value="factory_value")

        container.instances["service1"] = cached_instance
        container.RegisterSingletons({"service1": mock_factory})

        result = container.Get("service1")

        assert result == cached_instance
        mock_factory.assert_not_called()

    def test_GetWithInstanceTakesPrecedenceOverFactory_ShouldReturnInstance(self):
        """Test that Get returns cached instance even when factory exists."""
        container = Container()
        cached_instance = "cached_value"
        mock_factory = MagicMock(return_value="factory_value")

        container.instances["service1"] = cached_instance
        container.RegisterFactories({"service1": mock_factory})

        result = container.Get("service1")

        assert result == cached_instance
        mock_factory.assert_not_called()

    def test_GetWithSingletonTakesPrecedenceOverFactory_ShouldReturnSingleton(self):
        """Test that Get returns singleton when both singleton and factory exist."""
        container = Container()
        singleton_instance = "singleton_value"
        mock_singleton_factory = MagicMock(return_value=singleton_instance)
        mock_factory = MagicMock(return_value="factory_value")

        container.RegisterSingletons({"service1": mock_singleton_factory})
        container.RegisterFactories({"service1": mock_factory})

        result = container.Get("service1")

        assert result == singleton_instance
        mock_singleton_factory.assert_called_once_with(container)
        mock_factory.assert_not_called()

    def test_GetWithEmptyStringName_ShouldRaiseDependencyNotFoundException(self):
        """Test that Get raises exception when service name is empty string."""
        container = Container()

        with pytest.raises(DependencyNameNotFoundInContainerException):
            container.Get("")

    def test_RegisterSingletonsWithEmptyDict_ShouldNotChangeContainer(self):
        """Test that RegisterSingletons with empty dict does not change container."""
        container = Container()
        original_singletons = container.singletons.copy()

        container.RegisterSingletons({})

        assert container.singletons == original_singletons

    def test_RegisterFactoriesWithEmptyDict_ShouldNotChangeContainer(self):
        """Test that RegisterFactories with empty dict does not change container."""
        container = Container()
        original_factories = container.factories.copy()

        container.RegisterFactories({})

        assert container.factories == original_factories

    def test_RegisterSingletonsMultipleTimes_ShouldUpdateExistingFactories(self):
        """Test that multiple calls to RegisterSingletons update existing factories."""
        container = Container()
        mock_factory1 = MagicMock()
        mock_factory2 = MagicMock()

        container.RegisterSingletons({"service1": mock_factory1})
        container.RegisterSingletons({"service1": mock_factory2})

        assert container.singletons["service1"] == mock_factory2

    def test_RegisterFactoriesMultipleTimes_ShouldUpdateExistingFactories(self):
        """Test that multiple calls to RegisterFactories update existing factories."""
        container = Container()
        mock_factory1 = MagicMock()
        mock_factory2 = MagicMock()

        container.RegisterFactories({"service1": mock_factory1})
        container.RegisterFactories({"service1": mock_factory2})

        assert container.factories["service1"] == mock_factory2
