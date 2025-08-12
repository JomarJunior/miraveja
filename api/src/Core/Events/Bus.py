from src.Core.Events.Base import BaseEvent
from typing import Dict, Callable, List, Any

EventSubscriber = Callable[[BaseEvent], None]
EventClass = Any

class EventDispatcher:
    """
    Event dispatcher responsible for managing event subscribers and dispatching events.
    
    The EventDispatcher implements a publish-subscribe pattern where events can be
    registered with their corresponding subscribers (handlers) and then dispatched
    when they occur.
    
    Attributes:
        subscribers (Dict[EventClass, List[EventSubscriber]]): Dictionary mapping events to their subscribers.
    """
    
    def __init__(self):
        """
        Initialize the EventDispatcher with an empty subscribers dictionary.
        """
        self.subscribers: Dict[EventClass, List[EventSubscriber]] = {}

    def register(self, subscribers: Dict[EventClass, List[EventSubscriber]]):
        """
        Register multiple event subscribers at once.
        
        Args:
            subscribers (Dict[EventClass, List[EventSubscriber]]): Dictionary mapping events
                to lists of callable subscribers (event handlers).
                
        Example:
            >>> dispatcher.register({
            ...     UserCreatedEvent: [send_welcome_email, update_analytics],
            ...     ImageProcessedEvent: [generate_thumbnail, extract_metadata]
            ... })
        """
        self.subscribers.update(subscribers)

    def append_subscriber(self, event: EventClass, subscriber: EventSubscriber):
        """
        Add a single subscriber to an existing event.
        
        Args:
            event (EventClass): The event type to subscribe to.
            subscriber (EventSubscriber): The callable that will handle the event.
            
        Raises:
            KeyError: If the event type is not already registered.
            
        Example:
            >>> dispatcher.append_subscriber(UserCreatedEvent, log_user_creation)
        """
        self.subscribers[event].append(subscriber)

    def dispatch_all(self, events: List[BaseEvent]):
        """
        Dispatch multiple events in sequence.
        
        Args:
            events (List[BaseEvent]): List of event instances to dispatch.
            
        Note:
            Events are dispatched synchronously in the order they appear in the list.
            
        Example:
            >>> events = [UserCreatedEvent(user_id=123), EmailSentEvent(email_id=456)]
            >>> dispatcher.dispatch_all(events)
        """
        for event in events:
            self.dispatch(event)

    def dispatch(self, event: BaseEvent):
        """
        Dispatch a single event to all its registered subscribers.
        
        Args:
            event (BaseEvent): The event instance to dispatch.
            
        Note:
            If no subscribers are registered for the event type, the method
            silently returns without performing any action.
            
        Example:
            >>> event = UserCreatedEvent(user_id=123, email="user@example.com")
            >>> dispatcher.dispatch(event)
        """
        if event in self.subscribers:
            for subscriber in self.subscribers[event]:
                subscriber(event)


class EventEmitter:
    """
    Event emitter responsible for collecting and storing events that occur during execution.
    
    The EventEmitter follows the Domain-Driven Design pattern where domain entities
    can emit events that represent business-significant occurrences. These events
    are collected and can later be dispatched by an EventDispatcher.
    
    Attributes:
        events (List[BaseEvent]): List of events that have been emitted.
    """
    
    def __init__(self):
        """
        Initialize the EventEmitter with an empty events list.
        """
        self.events: List[BaseEvent] = []

    def emit_event(self, event: BaseEvent):
        """
        Emit an event by adding it to the internal events collection.
        
        Args:
            event (BaseEvent): The event instance to emit.

        Note:
            Events are stored in the order they were emitted and can be
            retrieved later for batch processing or dispatching.
            
        Example:
            >>> emitter = EventEmitter()
            >>> emitter.emit_event(ImageUploadedEvent(image_id=123, user_id=456))
            >>> emitter.emit_event(ThumbnailGeneratedEvent(image_id=123))
        """
        self.events.append(event)

    def release_events(self) -> List[BaseEvent]:
        """
        Release and return all stored events, clearing the internal events list.
        
        This method retrieves all currently stored events and clears the internal
        events collection, effectively releasing ownership of the events to the caller.
        
        Returns:
            List[BaseEvent]: A list containing all events that were stored in the bus.
                            Returns an empty list if no events were present.
        
        Note:
            After calling this method, the internal events list will be empty.
        """
        events: List[BaseEvent] = self.events
        self.events = []
        return events