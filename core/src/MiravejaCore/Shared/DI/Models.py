from typing import Any, Callable, Dict

from MiravejaCore.Shared.DI.Exceptions import DependencyNameNotFoundInContainerException


class Container:
    """
    A dependency injection container that manages singletons and factories.
    This class provides a simple dependency injection mechanism where services can be
    registered as either singletons (created once and reused) or factories (created
    on each request).
    Attributes:
        singletons (Dict[str, Callable]): Dictionary mapping service names to their
            singleton factory functions.
        factories (Dict[str, Callable]): Dictionary mapping service names to their
            factory functions.
        instances (Dict[str, Any]): Dictionary storing created singleton instances.
    Example:
        >>> container = Container()
        >>> container.register_singletons({'db': lambda c: DatabaseConnection()})
        >>> container.register_factories({'request': lambda c: HttpRequest()})
        >>> db_instance = container.get('db')  # Creates and caches instance
        >>> same_db = container.get('db')      # Returns cached instance
        >>> new_request = container.get('request')  # Creates new instance each time
    """

    def __init__(self):
        """Initialize the dependency injection container.

        Sets up empty dictionaries to store:
        - singletons: Factory functions for singleton instances
        - factories: Factory functions for transient instances
        - instances: Cached singleton instances

        Args:
            None

        Returns:
            None
        """
        self.singletons: Dict[str, Callable[["Container"], Any]] = {}
        self.factories: Dict[str, Callable[["Container"], Any]] = {}
        self.instances: Dict[str, Any] = {}

    @classmethod
    def FromConfig(cls, config: Any) -> "Container":
        """Create a container from a configuration object.

        Args:
            config: Any configuration object that has a model_dump() method (like Pydantic BaseModel)
        """
        container = cls()
        configDict = config.model_dump() if hasattr(config, "model_dump") else dict(config)
        container.instances.update(configDict)
        return container

    def RegisterSingletons(self, singleton: Dict[str, Callable[["Container"], Any]]):
        """
        Register singleton services in the dependency injection container.

        Args:
            singleton (Dict[str, Callable]): A dictionary mapping service names to their
                corresponding callable factory functions or classes. Each callable will
                be invoked only once to create a single instance that will be reused
                throughout the application lifecycle.

        Example:
            container.register_singletons({
                'database': DatabaseConnection,
                'logger': lambda: Logger('app.log'),
                'cache': RedisCache
            })
        """
        self.singletons.update(singleton)

    def RegisterFactories(self, factory: Dict[str, Callable[["Container"], Any]]):
        """
        Register factory functions for dependency injection.

        This method updates the container's factory registry with the provided
        factory functions. Each factory function is responsible for creating
        instances of specific types when requested.

        Args:
            factory (Dict[str, Callable]): A dictionary mapping service names
                to their corresponding factory functions. The keys are string
                identifiers for the services, and the values are callable
                factory functions that create instances of those services.

        Example:
            >>> container.register_factories({
            ...     'database': lambda: DatabaseConnection(),
            ...     'logger': lambda: Logger('app.log')
            ... })
        """
        self.factories.update(factory)

    def Get(self, name: str) -> Any:
        """
        Retrieve a service instance from the container.
        This method implements a hierarchical resolution strategy:
        1. First checks for existing instances (cached singletons)
        2. Then checks singleton factories and creates/caches the instance
        3. Finally checks regular factories and creates a new instance each time
        Args:
            name (str): The name/key of the service to retrieve from the container
        Returns:
            Any: The resolved service instance
        Raises:
            DependencyNameNotFoundInContainerException: When the requested service
                name is not registered in any of the container's registries
                (instances, singletons, or factories)
        """
        if name in self.instances:
            return self.instances[name]

        if name in self.singletons:
            instance = self.singletons[name](self)
            self.instances[name] = instance
            return instance

        if name in self.factories:
            return self.factories[name](self)

        raise DependencyNameNotFoundInContainerException(name)
