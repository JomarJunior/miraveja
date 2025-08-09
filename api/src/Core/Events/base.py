class BaseEvent:
    """
    Base class for all events in the system.
    This class provides a foundation for creating event objects with a unique name
    identifier. Events can be compared for equality and used as dictionary keys
    or in sets due to the implemented hash functionality.
    Attributes:
        name (str): The unique name identifier for the event.
    Methods:
        __eq__(other): Compares two BaseEvent instances for equality based on their names.
        __hash__(): Returns a hash value based on the event name for use in collections.
    Example:
        >>> event1 = BaseEvent("user_login")
        >>> event2 = BaseEvent("user_login")
        >>> event1 == event2
        True
        >>> {event1, event2}  # Can be used in sets
        {BaseEvent('user_login')}
    """

    def __init__(self, name: str):
        """
        Initialize the event with a name.

        Args:
            name (str): The name of the event.
        """
        self.name = name

    def __eq__(self, other: object) -> bool:
        """
        Compare two BaseEvent instances for equality.

        Two BaseEvent instances are considered equal if they have the same name.
        If the other object is not a BaseEvent instance, returns False.

        Args:
            other (object): The object to compare with this BaseEvent instance.

        Returns:
            bool: True if both objects are BaseEvent instances with the same name,
                  False otherwise.

        Examples:
            >>> event1 = BaseEvent("test_event")
            >>> event2 = BaseEvent("test_event")
            >>> event3 = BaseEvent("other_event")
            >>> event1 == event2
            True
            >>> event1 == event3
            False
            >>> event1 == "test_event"
            False
        """
        if isinstance(other, BaseEvent):
            return self.name == other.name
        return False
    
    def __hash__(self) -> int:
        """
        Return hash value for the event based on its name.

        This method enables the event to be used as a key in dictionaries
        and as an element in sets by providing a hash value derived from
        the event's name attribute.

        Returns:
            int: Hash value of the event's name.
        """
        return hash(self.name)