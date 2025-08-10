import pytest
from unittest.mock import Mock, call
from Core.Events.Base import BaseEvent
from Core.Events.Bus import EventDispatcher, EventEmitter

class MockEvent(BaseEvent):
    """Mock event class for testing purposes."""
    def __init__(self, name = "MockEvent", data=None):
        super().__init__(name)
        self.data = data

class TestEventDispatcher:
    """Test suite for the EventDispatcher class."""

    def test_init_creates_empty_subscribers_dict(self):
        """Test that EventDispatcher initialization creates empty subscribers dictionary."""
        dispatcher = EventDispatcher()
        
        assert dispatcher.subscribers == {}

    def test_register_updates_subscribers_dict(self):
        """Test that register updates the subscribers dictionary."""
        dispatcher = EventDispatcher()
        mock_subscriber = Mock()
        event_class = MockEvent
        
        subscribers = {event_class: [mock_subscriber]}
        dispatcher.register(subscribers)

        assert dispatcher.subscribers[event_class] == [mock_subscriber]

    def test_register_multiple_events_and_subscribers(self):
        """Test registering multiple events with multiple subscribers."""
        dispatcher = EventDispatcher()
        mock_subscriber1 = Mock()
        mock_subscriber2 = Mock()
        mock_subscriber3 = Mock()
        event_class1 = MockEvent
        event_class2 = type('AnotherMockEvent', (BaseEvent,), {})
        
        subscribers = {
            event_class1: [mock_subscriber1, mock_subscriber2],
            event_class2: [mock_subscriber3]
        }
        dispatcher.register(subscribers)
        
        assert dispatcher.subscribers[event_class1] == [mock_subscriber1, mock_subscriber2]
        assert dispatcher.subscribers[event_class2] == [mock_subscriber3]

    def test_register_overwrites_existing_subscribers(self):
        """Test that register overwrites existing subscribers for the same event."""
        dispatcher = EventDispatcher()
        old_subscriber = Mock()
        new_subscriber = Mock()
        event_class = MockEvent
        
        # Register initial subscriber
        dispatcher.subscribers[event_class] = [old_subscriber]
        
        # Register new subscribers (should overwrite)
        subscribers = {event_class: [new_subscriber]}
        dispatcher.register(subscribers)
        
        assert dispatcher.subscribers[event_class] == [new_subscriber]

    def test_append_subscriber_adds_to_existing_list(self):
        """Test that append_subscriber adds a subscriber to existing event."""
        dispatcher = EventDispatcher()
        existing_subscriber = Mock()
        new_subscriber = Mock()
        event_class = MockEvent
        
        # Setup existing subscriber
        dispatcher.subscribers[event_class] = [existing_subscriber]
        
        dispatcher.append_subscriber(event_class, new_subscriber)
        
        assert dispatcher.subscribers[event_class] == [existing_subscriber, new_subscriber]

    def test_append_subscriber_raises_keyerror_for_unknown_event(self):
        """Test that append_subscriber raises KeyError for unregistered events."""
        dispatcher = EventDispatcher()
        mock_subscriber = Mock()
        event_class = MockEvent
        
        with pytest.raises(KeyError):
            dispatcher.append_subscriber(event_class, mock_subscriber)

    def test_dispatch_calls_all_subscribers_for_event(self):
        """Test that dispatch calls all registered subscribers for an event."""
        dispatcher = EventDispatcher()
        mock_subscriber1 = Mock()
        mock_subscriber2 = Mock()
        event_instance = MockEvent(data="test")
        
        dispatcher.subscribers[event_instance] = [mock_subscriber1, mock_subscriber2]
        
        dispatcher.dispatch(event_instance)
        
        mock_subscriber1.assert_called_once_with(event_instance)
        mock_subscriber2.assert_called_once_with(event_instance)

    def test_dispatch_does_nothing_for_unregistered_event(self):
        """Test that dispatch silently returns for events with no subscribers."""
        dispatcher = EventDispatcher()
        event_instance = MockEvent(data="test")
        
        # This should not raise an exception
        dispatcher.dispatch(event_instance)

    def test_dispatch_with_empty_subscribers_list(self):
        """Test that dispatch handles empty subscribers list gracefully."""
        dispatcher = EventDispatcher()
        event_instance = MockEvent(data="test")
        
        dispatcher.subscribers[event_instance] = []
        
        # This should not raise an exception
        dispatcher.dispatch(event_instance)

    def test_dispatch_all_calls_dispatch_for_each_event(self):
        """Test that dispatch_all calls dispatch for each event in the list."""
        dispatcher = EventDispatcher()
        mock_subscriber = Mock()
        event1 = MockEvent(data="event1")
        event2 = MockEvent(data="event2")
        
        dispatcher.subscribers[event1] = [mock_subscriber]
        dispatcher.subscribers[event2] = [mock_subscriber]
        
        dispatcher.dispatch_all([event1, event2])
        
        expected_calls = [call(event1), call(event2)]
        assert mock_subscriber.call_args_list == expected_calls

    def test_dispatch_all_with_empty_list(self):
        """Test that dispatch_all handles empty event list gracefully."""
        dispatcher = EventDispatcher()
        
        # This should not raise an exception
        dispatcher.dispatch_all([])

    def test_dispatch_all_maintains_event_order(self):
        """Test that dispatch_all processes events in the correct order."""
        dispatcher = EventDispatcher()
        call_order = []
        
        def subscriber1(event):
            call_order.append(f"event1-{event.data}")
        
        def subscriber2(event):
            call_order.append(f"event2-{event.data}")
        
        event1 = MockEvent(data="first", name="event1")
        event2 = MockEvent(data="second", name="event2")

        dispatcher.subscribers[event1] = [subscriber1]
        dispatcher.subscribers[event2] = [subscriber2]
        
        dispatcher.dispatch_all([event1, event2])
        
        assert call_order == ["event1-first", "event2-second"]


class TestEventEmitter:
    """Test suite for the EventEmitter class."""

    def test_init_creates_empty_events_list(self):
        """Test that EventEmitter initialization creates empty events list."""
        emitter = EventEmitter()
        
        assert emitter.events == []

    def test_emit_event_adds_event_to_list(self):
        """Test that emit_event adds an event to the events list."""
        emitter = EventEmitter()
        event = MockEvent(data="test")
        
        emitter.emit_event(event)
        
        assert emitter.events == [event]

    def test_emit_event_multiple_events(self):
        """Test that emit_event can add multiple events maintaining order."""
        emitter = EventEmitter()
        event1 = MockEvent(data="first")
        event2 = MockEvent(data="second")
        event3 = MockEvent(data="third")
        
        emitter.emit_event(event1)
        emitter.emit_event(event2)
        emitter.emit_event(event3)
        
        assert emitter.events == [event1, event2, event3]

    def test_release_events_returns_all_events(self):
        """Test that release_events returns all stored events."""
        emitter = EventEmitter()
        event1 = MockEvent(data="first")
        event2 = MockEvent(data="second")
        
        emitter.emit_event(event1)
        emitter.emit_event(event2)
        
        released_events = emitter.release_events()
        
        assert released_events == [event1, event2]

    def test_release_events_clears_internal_list(self):
        """Test that release_events clears the internal events list."""
        emitter = EventEmitter()
        event = MockEvent(data="test")
        
        emitter.emit_event(event)
        emitter.release_events()
        
        assert emitter.events == []

    def test_release_events_with_empty_list(self):
        """Test that release_events returns empty list when no events exist."""
        emitter = EventEmitter()
        
        released_events = emitter.release_events()
        
        assert released_events == []

    def test_release_events_multiple_calls(self):
        """Test that multiple calls to release_events work correctly."""
        emitter = EventEmitter()
        event1 = MockEvent(data="first")
        event2 = MockEvent(data="second")
        
        emitter.emit_event(event1)
        first_release = emitter.release_events()
        
        emitter.emit_event(event2)
        second_release = emitter.release_events()
        
        assert first_release == [event1]
        assert second_release == [event2]
        assert emitter.events == []

    def test_event_emitter_integration_with_dispatcher(self):
        """Test integration between EventEmitter and EventDispatcher."""
        emitter = EventEmitter()
        dispatcher = EventDispatcher()
        mock_subscriber = Mock()
        
        event = MockEvent(data="integration_test")
        
        # Setup dispatcher
        dispatcher.subscribers[event] = [mock_subscriber]
        
        # Emit event
        emitter.emit_event(event)
        
        # Release and dispatch events
        events = emitter.release_events()
        dispatcher.dispatch_all(events)
        
        mock_subscriber.assert_called_once_with(event)
        assert emitter.events == []