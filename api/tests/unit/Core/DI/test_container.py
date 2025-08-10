import pytest
from unittest.mock import Mock, call
from Core.DI.Container import Container

class TestContainer:
    """Test suite for the Container dependency injection class."""
    
    def test_init_creates_empty_dictionaries(self):
        """Test that Container initialization creates empty dictionaries."""
        container = Container()
        
        assert container.singletons == {}
        assert container.factories == {}
        assert container.instances == {}
    
    def test_register_singletons_updates_registry(self):
        """Test that register_singletons updates the singletons dictionary."""
        container = Container()
        mock_factory = Mock()
        
        singletons = {'service1': mock_factory}
        container.register_singletons(singletons)
        
        assert container.singletons['service1'] is mock_factory
    
    def test_register_singletons_multiple_services(self):
        """Test registering multiple singleton services at once."""
        container = Container()
        mock_factory1 = Mock()
        mock_factory2 = Mock()
        
        singletons = {
            'service1': mock_factory1,
            'service2': mock_factory2
        }
        container.register_singletons(singletons)
        
        assert container.singletons['service1'] is mock_factory1
        assert container.singletons['service2'] is mock_factory2
    
    def test_register_factories_updates_registry(self):
        """Test that register_factories updates the factories dictionary."""
        container = Container()
        mock_factory = Mock()
        
        factories = {'service1': mock_factory}
        container.register_factories(factories)
        
        assert container.factories['service1'] is mock_factory
    
    def test_register_factories_multiple_services(self):
        """Test registering multiple factory services at once."""
        container = Container()
        mock_factory1 = Mock()
        mock_factory2 = Mock()
        
        factories = {
            'service1': mock_factory1,
            'service2': mock_factory2
        }
        container.register_factories(factories)
        
        assert container.factories['service1'] is mock_factory1
        assert container.factories['service2'] is mock_factory2
    
    def test_get_returns_existing_instance(self):
        """Test that get() returns existing cached instances."""
        container = Container()
        mock_instance = Mock()
        container.instances['service1'] = mock_instance
        
        result = container.get('service1')
        
        assert result is mock_instance
    
    def test_get_creates_singleton_instance(self):
        """Test that get() creates and caches singleton instances."""
        container = Container()
        mock_instance = Mock()
        mock_factory = Mock(return_value=mock_instance)
        container.singletons['service1'] = mock_factory
        
        result = container.get('service1')
        
        assert result is mock_instance
        assert container.instances['service1'] is mock_instance
        mock_factory.assert_called_once_with(container)
    
    def test_get_singleton_called_only_once(self):
        """Test that singleton factory is called only once for multiple gets."""
        container = Container()
        mock_instance = Mock()
        mock_factory = Mock(return_value=mock_instance)
        container.singletons['service1'] = mock_factory
        
        result1 = container.get('service1')
        result2 = container.get('service1')
        
        assert result1 is mock_instance
        assert result2 is mock_instance
        assert result1 is result2
        mock_factory.assert_called_once_with(container)
    
    def test_get_creates_factory_instance(self):
        """Test that get() creates new instances for factories."""
        container = Container()
        mock_instance = Mock()
        mock_factory = Mock(return_value=mock_instance)
        container.factories['service1'] = mock_factory
        
        result = container.get('service1')
        
        assert result is mock_instance
        mock_factory.assert_called_once_with(container)
        assert 'service1' not in container.instances
    
    def test_get_factory_called_multiple_times(self):
        """Test that factory is called each time for multiple gets."""
        container = Container()
        mock_instance1 = Mock()
        mock_instance2 = Mock()
        mock_factory = Mock(side_effect=[mock_instance1, mock_instance2])
        container.factories['service1'] = mock_factory
        
        result1 = container.get('service1')
        result2 = container.get('service1')
        
        assert result1 is mock_instance1
        assert result2 is mock_instance2
        assert mock_factory.call_count == 2
        mock_factory.assert_has_calls([call(container), call(container)])
    
    def test_get_resolution_hierarchy(self):
        """Test that get() follows the correct resolution hierarchy."""
        container = Container()
        
        # Set up all three registries for the same service name
        cached_instance = Mock(name='cached')
        singleton_instance = Mock(name='singleton')
        factory_instance = Mock(name='factory')
        
        singleton_factory = Mock(return_value=singleton_instance)
        factory_factory = Mock(return_value=factory_instance)
        
        container.instances['service1'] = cached_instance
        container.singletons['service1'] = singleton_factory
        container.factories['service1'] = factory_factory
        
        result = container.get('service1')
        
        # Should return cached instance and not call any factories
        assert result is cached_instance
        singleton_factory.assert_not_called()
        factory_factory.assert_not_called()
    
    def test_get_singleton_over_factory(self):
        """Test that singletons take precedence over factories."""
        container = Container()
        
        singleton_instance = Mock(name='singleton')
        factory_instance = Mock(name='factory')
        
        singleton_factory = Mock(return_value=singleton_instance)
        factory_factory = Mock(return_value=factory_instance)
        
        container.singletons['service1'] = singleton_factory
        container.factories['service1'] = factory_factory
        
        result = container.get('service1')
        
        # Should return singleton instance and not call factory
        assert result is singleton_instance
        singleton_factory.assert_called_once_with(container)
        factory_factory.assert_not_called()
        assert container.instances['service1'] is singleton_instance
    
    def test_get_unknown_service_returns_none(self):
        """Test that get() returns None for unknown service names."""
        container = Container()
        
        result = container.get('unknown_service')
        
        assert result is None
    
    def test_factory_receives_container_reference(self):
        """Test that factory functions receive the container as parameter."""
        container = Container()
        
        def factory_function(c):
            assert c is container
            return Mock()
        
        container.singletons['service1'] = factory_function
        container.get('service1')
        
        # Test passes if no assertion error is raised
    
    def test_multiple_services_isolation(self):
        """Test that different services are isolated from each other."""
        container = Container()
        
        instance1 = Mock(name='instance1')
        instance2 = Mock(name='instance2')
        
        factory1 = Mock(return_value=instance1)
        factory2 = Mock(return_value=instance2)
        
        container.singletons['service1'] = factory1
        container.singletons['service2'] = factory2
        
        result1 = container.get('service1')
        result2 = container.get('service2')
        
        assert result1 is instance1
        assert result2 is instance2
        assert result1 is not result2
        factory1.assert_called_once_with(container)
        factory2.assert_called_once_with(container)
