import json
import pytest
from typing import Any, ClassVar, Dict
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import jsonschema
from pydantic import ValidationError

from MiravejaCore.Shared.Events.Domain.Services import (
    EventValidatorService,
    EventRegistry,
    EventDeserializerService,
    EventExceptionOccurred,
    EventFactory,
    eventRegistry,
)
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent, ISchemaRegistry
from MiravejaCore.Shared.Events.Domain.Exceptions import (
    EventAlreadyRegisteredError,
    EventNotFoundError,
    InvalidJsonStringError,
    MissingEventTypeError,
    MissingEventVersionError,
    SchemaValidationError,
)
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Errors.Models import DomainException
from MiravejaCore.Shared.Identifiers.Models import EventId


class MockDomainEvent(DomainEvent):
    """Mock domain event for testing."""

    type: ClassVar[str] = "test.event"
    aggregateType: str = "test"
    aggregateId: str = "123"
    version: ClassVar[int] = 1
    testField: str = "test_value"


class MockDomainEventV2(DomainEvent):
    """Mock domain event version 2 for testing."""

    type: ClassVar[str] = "test.event.v2"
    aggregateType: str = "test"
    aggregateId: str = "456"
    version: ClassVar[int] = 2
    testField: str = "test_value_v2"


class TestEventValidatorService:
    """Test cases for EventValidatorService."""

    def CreateMockSchemaRegistry(self) -> ISchemaRegistry:
        """Create a mock schema registry for testing."""
        mockRegistry = AsyncMock(spec=ISchemaRegistry)
        return mockRegistry

    def CreateMockLogger(self) -> ILogger:
        """Create a mock logger for testing."""
        mockLogger = Mock(spec=ILogger)
        mockLogger.Error = Mock()
        mockLogger.Info = Mock()
        return mockLogger

    @pytest.mark.asyncio
    async def test_InitializeWithValidDependencies_ShouldSetCorrectValues(self):
        """Test that EventValidatorService initializes with valid dependencies."""
        # Arrange
        mockSchemaRegistry = self.CreateMockSchemaRegistry()
        mockLogger = self.CreateMockLogger()

        # Act
        service = EventValidatorService(schemaRegistry=mockSchemaRegistry, logger=mockLogger)

        # Assert
        assert service._schemaRegistry == mockSchemaRegistry
        assert service._logger == mockLogger

    @pytest.mark.asyncio
    async def test_ValidateEventWithValidData_ShouldPassValidation(self):
        """Test that ValidateEvent passes validation with valid event data."""
        # Arrange
        mockSchemaRegistry = self.CreateMockSchemaRegistry()
        mockLogger = self.CreateMockLogger()
        mockSchema = {"type": "object", "properties": {"testField": {"type": "string"}}}
        mockSchemaRegistry.GetSchema.return_value = mockSchema

        eventData = {"type": "test.event", "version": 1, "payload": {"testField": "test_value"}}

        service = EventValidatorService(schemaRegistry=mockSchemaRegistry, logger=mockLogger)

        # Act
        await service.ValidateEvent(eventData)

        # Assert
        mockSchemaRegistry.GetSchema.assert_called_once_with("test.event", 1)
        mockLogger.Info.assert_called_once_with("Event of type 'test.event' and version '1' validated successfully.")

    @pytest.mark.asyncio
    async def test_ValidateEventWithMissingType_ShouldRaiseMissingEventTypeError(self):
        """Test that ValidateEvent raises MissingEventTypeError when type is missing."""
        # Arrange
        mockSchemaRegistry = self.CreateMockSchemaRegistry()
        mockLogger = self.CreateMockLogger()
        eventData = {"version": 1, "payload": {"testField": "test_value"}}

        service = EventValidatorService(schemaRegistry=mockSchemaRegistry, logger=mockLogger)

        # Act & Assert
        with pytest.raises(MissingEventTypeError):
            await service.ValidateEvent(eventData)

        mockLogger.Error.assert_called_once_with("Event data missing 'type' field.")

    @pytest.mark.asyncio
    async def test_ValidateEventWithMissingVersion_ShouldRaiseMissingEventVersionError(self):
        """Test that ValidateEvent raises MissingEventVersionError when version is missing."""
        # Arrange
        mockSchemaRegistry = self.CreateMockSchemaRegistry()
        mockLogger = self.CreateMockLogger()
        eventData = {"type": "test.event", "payload": {"testField": "test_value"}}

        service = EventValidatorService(schemaRegistry=mockSchemaRegistry, logger=mockLogger)

        # Act & Assert
        with pytest.raises(MissingEventVersionError):
            await service.ValidateEvent(eventData)

        mockLogger.Error.assert_called_once_with("Event data missing 'version' field.")

    @pytest.mark.asyncio
    async def test_ValidateEventWithMissingPayload_ShouldRaiseSchemaValidationError(self):
        """Test that ValidateEvent raises SchemaValidationError when payload is missing."""
        # Arrange
        mockSchemaRegistry = self.CreateMockSchemaRegistry()
        mockLogger = self.CreateMockLogger()
        mockSchema = {"type": "object", "properties": {"testField": {"type": "string"}}}
        mockSchemaRegistry.GetSchema.return_value = mockSchema

        eventData = {"type": "test.event", "version": 1}

        service = EventValidatorService(schemaRegistry=mockSchemaRegistry, logger=mockLogger)

        # Act & Assert
        with pytest.raises(SchemaValidationError) as exc_info:
            await service.ValidateEvent(eventData)

        assert "Event data missing 'payload' field." in str(exc_info.value)
        mockLogger.Error.assert_called_once_with("Event data missing 'payload' field.")

    @pytest.mark.asyncio
    async def test_ValidateEventWithInvalidPayload_ShouldRaiseSchemaValidationError(self):
        """Test that ValidateEvent raises SchemaValidationError when payload fails schema validation."""
        # Arrange
        mockSchemaRegistry = self.CreateMockSchemaRegistry()
        mockLogger = self.CreateMockLogger()
        mockSchema = {"type": "object", "properties": {"testField": {"type": "number"}}, "required": ["testField"]}
        mockSchemaRegistry.GetSchema.return_value = mockSchema

        eventData = {"type": "test.event", "version": 1, "payload": {"testField": "invalid_string"}}

        service = EventValidatorService(schemaRegistry=mockSchemaRegistry, logger=mockLogger)

        # Act & Assert
        with pytest.raises(SchemaValidationError):
            await service.ValidateEvent(eventData)

        assert mockLogger.Error.call_count == 1

    @pytest.mark.asyncio
    async def test_ValidateEventWithEmptyPayload_ShouldPassIfSchemaAllows(self):
        """Test that ValidateEvent passes with empty payload if schema allows it."""
        # Arrange
        mockSchemaRegistry = self.CreateMockSchemaRegistry()
        mockLogger = self.CreateMockLogger()
        mockSchema = {"type": "object", "properties": {}}
        mockSchemaRegistry.GetSchema.return_value = mockSchema

        eventData = {"type": "test.event", "version": 1, "payload": {}}

        service = EventValidatorService(schemaRegistry=mockSchemaRegistry, logger=mockLogger)

        # Act
        await service.ValidateEvent(eventData)

        # Assert
        mockSchemaRegistry.GetSchema.assert_called_once_with("test.event", 1)
        mockLogger.Info.assert_called_once()


class TestEventRegistry:
    """Test cases for EventRegistry model."""

    def CreateMockLogger(self) -> ILogger:
        """Create a mock logger for testing."""
        mockLogger = Mock(spec=ILogger)
        mockLogger.Error = Mock()
        mockLogger.Info = Mock()
        mockLogger.Debug = Mock()
        return mockLogger

    def test_InitializeWithDefaults_ShouldSetCorrectDefaults(self):
        """Test that EventRegistry initializes with correct default values."""
        # Act
        registry = EventRegistry()

        # Assert
        assert isinstance(registry._eventRegistry, dict)
        assert len(registry._eventRegistry) == 0
        assert registry.logger is None

    def test_AttachLoggerWithValidLogger_ShouldSetLogger(self):
        """Test that AttachLogger sets the logger correctly."""
        # Arrange
        registry = EventRegistry()
        mockLogger = self.CreateMockLogger()

        # Act
        registry.AttachLogger(mockLogger)

        # Assert
        assert registry.logger == mockLogger
        mockLogger.Info.assert_called_once_with("Logger attached to EventRegistry.")
        mockLogger.Debug.assert_called_once()

    def test_RegisterEventWithNewEvent_ShouldRegisterSuccessfully(self):
        """Test that RegisterEvent registers a new event successfully."""
        # Arrange
        registry = EventRegistry()
        mockLogger = self.CreateMockLogger()
        registry.AttachLogger(mockLogger)

        # Act
        @registry.RegisterEvent(eventType="new.event", eventVersion=1)
        class NewEvent(DomainEvent):
            type: ClassVar[str] = "new.event"
            aggregateType: str = "test"
            aggregateId: str = "123"
            version: ClassVar[int] = 1

        # Assert
        assert ("new.event", 1) in registry._eventRegistry
        assert registry._eventRegistry[("new.event", 1)] == NewEvent

    def test_RegisterEventWithDuplicateEvent_ShouldRaiseEventAlreadyRegisteredError(self):
        """Test that RegisterEvent raises EventAlreadyRegisteredError for duplicate registration."""
        # Arrange
        registry = EventRegistry()
        mockLogger = self.CreateMockLogger()
        registry.AttachLogger(mockLogger)

        @registry.RegisterEvent(eventType="duplicate.event", eventVersion=1)
        class FirstEvent(DomainEvent):
            type: ClassVar[str] = "duplicate.event"
            aggregateType: str = "test"
            aggregateId: str = "123"
            version: ClassVar[int] = 1

        # Act & Assert
        with pytest.raises(EventAlreadyRegisteredError) as exc_info:

            @registry.RegisterEvent(eventType="duplicate.event", eventVersion=1)
            class SecondEvent(DomainEvent):
                type: ClassVar[str] = "duplicate.event"
                aggregateType: str = "test"
                aggregateId: str = "456"
                version: ClassVar[int] = 1

        assert "duplicate.event" in str(exc_info.value)
        assert "1" in str(exc_info.value)

    def test_GetEventClassWithRegisteredEvent_ShouldReturnEventClass(self):
        """Test that GetEventClass returns the registered event class."""
        # Arrange
        registry = EventRegistry()

        @registry.RegisterEvent(eventType="registered.event", eventVersion=1)
        class RegisteredEvent(DomainEvent):
            type: ClassVar[str] = "registered.event"
            aggregateType: str = "test"
            aggregateId: str = "123"
            version: ClassVar[int] = 1

        # Act
        eventClass = registry.GetEventClass("registered.event", 1)

        # Assert
        assert eventClass == RegisteredEvent

    def test_GetEventClassWithUnregisteredEvent_ShouldRaiseEventNotFoundError(self):
        """Test that GetEventClass raises EventNotFoundError for unregistered event."""
        # Arrange
        registry = EventRegistry()

        # Act & Assert
        with pytest.raises(EventNotFoundError) as exc_info:
            registry.GetEventClass("unregistered.event", 1)

        assert "unregistered.event" in str(exc_info.value)
        assert "1" in str(exc_info.value)

    def test_GetEventClassFromTopicWithValidTopic_ShouldReturnEventClass(self):
        """Test that GetEventClassFromTopic returns the event class from topic name."""
        # Arrange
        registry = EventRegistry()

        @registry.RegisterEvent(eventType="topic.event", eventVersion=1)
        class TopicEvent(DomainEvent):
            type: ClassVar[str] = "topic.event"
            aggregateType: str = "test"
            aggregateId: str = "123"
            version: ClassVar[int] = 1

        # Act
        eventClass = registry.GetEventClassFromTopic("miraveja.topic.event.v1")

        # Assert
        assert eventClass == TopicEvent

    def test_GetEventClassFromTopicWithMultipartEventType_ShouldParseCorrectly(self):
        """Test that GetEventClassFromTopic handles multi-part event types."""
        # Arrange
        registry = EventRegistry()

        @registry.RegisterEvent(eventType="user.profile.updated", eventVersion=2)
        class UserProfileUpdatedEvent(DomainEvent):
            type: ClassVar[str] = "user.profile.updated"
            aggregateType: str = "user"
            aggregateId: str = "123"
            version: ClassVar[int] = 2

        # Act
        eventClass = registry.GetEventClassFromTopic("miraveja.user.profile.updated.v2")

        # Assert
        assert eventClass == UserProfileUpdatedEvent

    def test_RegisterEventWithoutLogger_ShouldRegisterWithoutError(self):
        """Test that RegisterEvent works without attached logger."""
        # Arrange
        registry = EventRegistry()

        # Act
        @registry.RegisterEvent(eventType="no.logger.event", eventVersion=1)
        class NoLoggerEvent(DomainEvent):
            type: ClassVar[str] = "no.logger.event"
            aggregateType: str = "test"
            aggregateId: str = "123"
            version: ClassVar[int] = 1

        # Assert
        assert ("no.logger.event", 1) in registry._eventRegistry


class TestEventDeserializerService:
    """Test cases for EventDeserializerService."""

    def CreateMockLogger(self) -> ILogger:
        """Create a mock logger for testing."""
        mockLogger = Mock(spec=ILogger)
        mockLogger.Error = Mock()
        mockLogger.Info = Mock()
        return mockLogger

    def test_InitializeWithValidDependencies_ShouldSetCorrectValues(self):
        """Test that EventDeserializerService initializes with valid dependencies."""
        # Arrange
        mockRegistry = EventRegistry()
        mockLogger = self.CreateMockLogger()

        # Act
        service = EventDeserializerService(mockRegistry, mockLogger)

        # Assert
        assert service._eventRegistry == mockRegistry
        assert service._logger == mockLogger

    def test_DeserializeEventWithValidData_ShouldReturnEventInstance(self):
        """Test that DeserializeEvent returns a valid event instance."""
        # Arrange
        mockRegistry = EventRegistry()
        mockLogger = self.CreateMockLogger()

        @mockRegistry.RegisterEvent(eventType="deserialize.event", eventVersion=1)
        class DeserializeEvent(DomainEvent):
            type: ClassVar[str] = "deserialize.event"
            aggregateType: str = "test"
            aggregateId: str = "123"
            version: ClassVar[int] = 1
            testField: str = "default"

        eventData = {
            "type": "deserialize.event",
            "version": 1,
            "payload": {"aggregateType": "test", "aggregateId": "123", "testField": "test_value"},
        }

        service = EventDeserializerService(mockRegistry, mockLogger)

        # Act
        result = service.DeserializeEvent(eventData)

        # Assert
        assert isinstance(result, DeserializeEvent)
        assert result.testField == "test_value"
        assert result.aggregateId == "123"
        mockLogger.Info.assert_called_once_with(
            "Event of type 'deserialize.event' and version '1' deserialized successfully."
        )

    def test_DeserializeEventWithMissingType_ShouldRaiseMissingEventTypeError(self):
        """Test that DeserializeEvent raises MissingEventTypeError when type is missing."""
        # Arrange
        mockRegistry = EventRegistry()
        mockLogger = self.CreateMockLogger()
        eventData = {"version": 1, "payload": {"testField": "test_value"}}

        service = EventDeserializerService(mockRegistry, mockLogger)

        # Act & Assert
        with pytest.raises(MissingEventTypeError):
            service.DeserializeEvent(eventData)

        mockLogger.Error.assert_called_once_with("Event data missing 'type' field.")

    def test_DeserializeEventWithMissingVersion_ShouldRaiseMissingEventVersionError(self):
        """Test that DeserializeEvent raises MissingEventVersionError when version is missing."""
        # Arrange
        mockRegistry = EventRegistry()
        mockLogger = self.CreateMockLogger()
        eventData = {"type": "test.event", "payload": {"testField": "test_value"}}

        service = EventDeserializerService(mockRegistry, mockLogger)

        # Act & Assert
        with pytest.raises(MissingEventVersionError):
            service.DeserializeEvent(eventData)

        mockLogger.Error.assert_called_once_with("Event data missing 'version' field.")

    def test_DeserializeEventWithMissingPayload_ShouldRaiseSchemaValidationError(self):
        """Test that DeserializeEvent raises SchemaValidationError when payload is missing."""
        # Arrange
        mockRegistry = EventRegistry()
        mockLogger = self.CreateMockLogger()
        eventData = {"type": "test.event", "version": 1}

        service = EventDeserializerService(mockRegistry, mockLogger)

        # Act & Assert
        with pytest.raises(SchemaValidationError) as exc_info:
            service.DeserializeEvent(eventData)

        assert "Event data missing 'payload' field." in str(exc_info.value)
        mockLogger.Error.assert_called_once_with("Event data missing 'payload' field.")

    def test_DeserializeEventWithUnregisteredEvent_ShouldRaiseEventNotFoundError(self):
        """Test that DeserializeEvent raises EventNotFoundError for unregistered event type."""
        # Arrange
        mockRegistry = EventRegistry()
        mockLogger = self.CreateMockLogger()
        eventData = {
            "type": "unregistered.event",
            "version": 1,
            "payload": {"aggregateType": "test", "aggregateId": "123"},
        }

        service = EventDeserializerService(mockRegistry, mockLogger)

        # Act & Assert
        with pytest.raises(EventNotFoundError):
            service.DeserializeEvent(eventData)


class TestEventExceptionOccurred:
    """Test cases for EventExceptionOccurred domain event."""

    def test_InitializeWithValidData_ShouldSetCorrectValues(self):
        """Test that EventExceptionOccurred initializes with valid data."""
        # Act
        event = EventExceptionOccurred(
            aggregateType="event", aggregateId="", exceptionMessage="Test error", exceptionCode=500
        )

        # Assert
        assert event.type == "event.exception.occurred"
        assert event.aggregateType == "event"
        assert event.aggregateId == ""
        assert event.version == 1
        assert event.exceptionMessage == "Test error"
        assert event.exceptionCode == 500
        assert isinstance(event.id, EventId)

    def test_CreateWithValidParameters_ShouldReturnEventInstance(self):
        """Test that Create factory method returns a valid event instance."""
        # Act
        event = EventExceptionOccurred.Create(exceptionMessage="Factory error", exceptionCode=400)

        # Assert
        assert isinstance(event, EventExceptionOccurred)
        assert event.exceptionMessage == "Factory error"
        assert event.exceptionCode == 400
        assert event.aggregateType == "event"
        assert event.aggregateId == ""

    def test_CreateWithEmptyMessage_ShouldSetEmptyMessage(self):
        """Test that Create accepts empty exception message."""
        # Act
        event = EventExceptionOccurred.Create(exceptionMessage="", exceptionCode=0)

        # Assert
        assert event.exceptionMessage == ""
        assert event.exceptionCode == 0

    def test_ToKafkaMessageWithEventData_ShouldReturnCorrectFormat(self):
        """Test that ToKafkaMessage returns correct Kafka message format."""
        # Arrange
        event = EventExceptionOccurred.Create(exceptionMessage="Kafka test", exceptionCode=503)

        # Act
        kafkaMessage = event.ToKafkaMessage()

        # Assert
        assert kafkaMessage["type"] == "event.exception.occurred"
        assert kafkaMessage["version"] == 1
        assert "payload" in kafkaMessage
        assert kafkaMessage["payload"]["exceptionMessage"] == "Kafka test"
        assert kafkaMessage["payload"]["exceptionCode"] == 503


class TestEventFactory:
    """Test cases for EventFactory."""

    def CreateMockDeserializerService(self) -> EventDeserializerService:
        """Create a mock deserializer service for testing."""
        mockService = Mock(spec=EventDeserializerService)
        return mockService

    def CreateMockValidatorService(self) -> EventValidatorService:
        """Create a mock validator service for testing."""
        mockService = AsyncMock(spec=EventValidatorService)
        return mockService

    @pytest.mark.asyncio
    async def test_InitializeWithValidDependencies_ShouldSetCorrectValues(self):
        """Test that EventFactory initializes with valid dependencies."""
        # Arrange
        mockDeserializer = self.CreateMockDeserializerService()
        mockValidator = self.CreateMockValidatorService()

        # Act
        factory = EventFactory(deserializerService=mockDeserializer, validatorService=mockValidator)

        # Assert
        assert factory._deserializerService == mockDeserializer
        assert factory._validatorService == mockValidator

    @pytest.mark.asyncio
    async def test_CreateFromDataWithValidData_ShouldReturnEventInstance(self):
        """Test that CreateFromData validates and deserializes event data."""
        # Arrange
        mockDeserializer = self.CreateMockDeserializerService()
        mockValidator = self.CreateMockValidatorService()
        mockEvent = MockDomainEvent(aggregateType="test", aggregateId="123")

        mockValidator.ValidateEvent = AsyncMock()
        mockDeserializer.DeserializeEvent.return_value = mockEvent

        eventData = {"type": "test.event", "version": 1, "payload": {"testField": "test_value"}}

        factory = EventFactory(deserializerService=mockDeserializer, validatorService=mockValidator)

        # Act
        result = await factory.CreateFromData(eventData)

        # Assert
        mockValidator.ValidateEvent.assert_called_once_with(eventData)
        mockDeserializer.DeserializeEvent.assert_called_once_with(eventData)
        assert result == mockEvent

    @pytest.mark.asyncio
    async def test_CreateFromDataWithInvalidData_ShouldRaiseValidationError(self):
        """Test that CreateFromData raises validation errors from validator."""
        # Arrange
        mockDeserializer = self.CreateMockDeserializerService()
        mockValidator = self.CreateMockValidatorService()

        mockValidator.ValidateEvent.side_effect = SchemaValidationError("Invalid schema")

        eventData = {"type": "test.event", "version": 1, "payload": {"testField": "invalid"}}

        factory = EventFactory(deserializerService=mockDeserializer, validatorService=mockValidator)

        # Act & Assert
        with pytest.raises(SchemaValidationError):
            await factory.CreateFromData(eventData)

    @pytest.mark.asyncio
    async def test_CreateFromJsonWithValidJson_ShouldReturnEventInstance(self):
        """Test that CreateFromJson parses JSON and creates event instance."""
        # Arrange
        mockDeserializer = self.CreateMockDeserializerService()
        mockValidator = self.CreateMockValidatorService()
        mockEvent = MockDomainEvent(aggregateType="test", aggregateId="123")

        mockValidator.ValidateEvent = AsyncMock()
        mockDeserializer.DeserializeEvent.return_value = mockEvent

        eventJson = '{"type": "test.event", "version": 1, "payload": {"testField": "test_value"}}'

        factory = EventFactory(deserializerService=mockDeserializer, validatorService=mockValidator)

        # Act
        result = await factory.CreateFromJson(eventJson)

        # Assert
        assert result == mockEvent
        mockValidator.ValidateEvent.assert_called_once()
        mockDeserializer.DeserializeEvent.assert_called_once()

    @pytest.mark.asyncio
    async def test_CreateFromJsonWithInvalidJson_ShouldRaiseInvalidJsonStringError(self):
        """Test that CreateFromJson raises InvalidJsonStringError for malformed JSON."""
        # Arrange
        mockDeserializer = self.CreateMockDeserializerService()
        mockValidator = self.CreateMockValidatorService()

        invalidJson = '{"type": "test.event", "version": 1, invalid json'

        factory = EventFactory(deserializerService=mockDeserializer, validatorService=mockValidator)

        # Act & Assert
        with pytest.raises(InvalidJsonStringError) as exc_info:
            await factory.CreateFromJson(invalidJson)

        assert "Invalid JSON string" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_CreateFromJsonWithEmptyString_ShouldRaiseInvalidJsonStringError(self):
        """Test that CreateFromJson raises InvalidJsonStringError for empty JSON string."""
        # Arrange
        mockDeserializer = self.CreateMockDeserializerService()
        mockValidator = self.CreateMockValidatorService()

        factory = EventFactory(deserializerService=mockDeserializer, validatorService=mockValidator)

        # Act & Assert
        with pytest.raises(InvalidJsonStringError):
            await factory.CreateFromJson("")

    @pytest.mark.asyncio
    async def test_CreateFromDomainExceptionWithValidException_ShouldReturnEventExceptionOccurred(self):
        """Test that CreateFromDomainException creates EventExceptionOccurred from DomainException."""
        # Arrange
        mockDeserializer = self.CreateMockDeserializerService()
        mockValidator = self.CreateMockValidatorService()

        domainException = DomainException("Test exception message", code=404)

        factory = EventFactory(deserializerService=mockDeserializer, validatorService=mockValidator)

        # Act
        result = await factory.CreateFromDomainException(domainException)

        # Assert
        assert isinstance(result, EventExceptionOccurred)
        assert result.exceptionMessage == "Test exception message"
        assert result.exceptionCode == 404

    @pytest.mark.asyncio
    async def test_CreateFromDomainExceptionWithZeroCode_ShouldCreateEvent(self):
        """Test that CreateFromDomainException handles zero error code."""
        # Arrange
        mockDeserializer = self.CreateMockDeserializerService()
        mockValidator = self.CreateMockValidatorService()

        domainException = DomainException("Zero code exception", code=0)

        factory = EventFactory(deserializerService=mockDeserializer, validatorService=mockValidator)

        # Act
        result = await factory.CreateFromDomainException(domainException)

        # Assert
        assert result.exceptionMessage == "Zero code exception"
        assert result.exceptionCode == 0


class TestEventRegistryGlobalInstance:
    """Test cases for the global eventRegistry instance."""

    def test_GlobalEventRegistryInstance_ShouldExist(self):
        """Test that global eventRegistry instance exists."""
        # Assert
        assert eventRegistry is not None
        assert isinstance(eventRegistry, EventRegistry)

    def test_GlobalEventRegistryInstance_ShouldHaveEventExceptionOccurredRegistered(self):
        """Test that EventExceptionOccurred is registered in global registry."""
        # Act
        eventClass = eventRegistry.GetEventClass("event.exception.occurred", 1)

        # Assert
        assert eventClass == EventExceptionOccurred


class TestEventValidatorServiceEdgeCases:
    """Test edge cases for EventValidatorService."""

    def CreateMockSchemaRegistry(self) -> ISchemaRegistry:
        """Create a mock schema registry for testing."""
        mockRegistry = AsyncMock(spec=ISchemaRegistry)
        return mockRegistry

    def CreateMockLogger(self) -> ILogger:
        """Create a mock logger for testing."""
        mockLogger = Mock(spec=ILogger)
        mockLogger.Error = Mock()
        mockLogger.Info = Mock()
        return mockLogger

    @pytest.mark.asyncio
    async def test_ValidateEventWithNullPayloadValue_ShouldRaiseSchemaValidationError(self):
        """Test that ValidateEvent raises error when payload is None."""
        # Arrange
        mockSchemaRegistry = self.CreateMockSchemaRegistry()
        mockLogger = self.CreateMockLogger()
        mockSchema = {"type": "object"}
        mockSchemaRegistry.GetSchema.return_value = mockSchema

        eventData = {"type": "test.event", "version": 1, "payload": None}

        service = EventValidatorService(schemaRegistry=mockSchemaRegistry, logger=mockLogger)

        # Act & Assert
        with pytest.raises(SchemaValidationError):
            await service.ValidateEvent(eventData)

    @pytest.mark.asyncio
    async def test_ValidateEventWithComplexSchema_ShouldValidateCorrectly(self):
        """Test that ValidateEvent handles complex nested schemas."""
        # Arrange
        mockSchemaRegistry = self.CreateMockSchemaRegistry()
        mockLogger = self.CreateMockLogger()
        mockSchema = {
            "type": "object",
            "properties": {"nested": {"type": "object", "properties": {"field": {"type": "string"}}}},
        }
        mockSchemaRegistry.GetSchema.return_value = mockSchema

        eventData = {"type": "test.event", "version": 1, "payload": {"nested": {"field": "value"}}}

        service = EventValidatorService(schemaRegistry=mockSchemaRegistry, logger=mockLogger)

        # Act
        await service.ValidateEvent(eventData)

        # Assert
        mockLogger.Info.assert_called_once()


class TestEventDeserializerServiceEdgeCases:
    """Test edge cases for EventDeserializerService."""

    def CreateMockLogger(self) -> ILogger:
        """Create a mock logger for testing."""
        mockLogger = Mock(spec=ILogger)
        mockLogger.Error = Mock()
        mockLogger.Info = Mock()
        return mockLogger

    def test_DeserializeEventWithInvalidPayloadStructure_ShouldRaiseValidationError(self):
        """Test that DeserializeEvent raises validation error for invalid payload structure."""
        # Arrange
        mockRegistry = EventRegistry()
        mockLogger = self.CreateMockLogger()

        @mockRegistry.RegisterEvent(eventType="strict.event", eventVersion=1)
        class StrictEvent(DomainEvent):
            type: ClassVar[str] = "strict.event"
            aggregateType: str
            aggregateId: str
            version: ClassVar[int] = 1
            requiredField: str

        eventData = {
            "type": "strict.event",
            "version": 1,
            "payload": {"aggregateType": "test", "aggregateId": "123"},  # Missing requiredField
        }

        service = EventDeserializerService(mockRegistry, mockLogger)

        # Act & Assert
        with pytest.raises(ValidationError):
            service.DeserializeEvent(eventData)


class TestEventFactoryEdgeCases:
    """Test edge cases for EventFactory."""

    @pytest.mark.asyncio
    async def test_CreateFromJsonWithNullJson_ShouldRaiseMissingEventTypeError(self):
        """Test that CreateFromJson handles null JSON value (validates to None)."""
        # Arrange
        mockDeserializer = Mock(spec=EventDeserializerService)
        mockValidator = AsyncMock(spec=EventValidatorService)
        mockValidator.ValidateEvent.side_effect = MissingEventTypeError()

        factory = EventFactory(deserializerService=mockDeserializer, validatorService=mockValidator)

        # Act & Assert - "null" is valid JSON that deserializes to None, which then fails validation
        with pytest.raises(MissingEventTypeError):
            await factory.CreateFromJson("null")

    @pytest.mark.asyncio
    async def test_CreateFromJsonWithArrayJson_ShouldProcessArray(self):
        """Test that CreateFromJson can handle JSON array (though it may fail validation)."""
        # Arrange
        mockDeserializer = Mock(spec=EventDeserializerService)
        mockValidator = AsyncMock(spec=EventValidatorService)
        mockValidator.ValidateEvent.side_effect = MissingEventTypeError()

        factory = EventFactory(deserializerService=mockDeserializer, validatorService=mockValidator)

        # Act & Assert
        with pytest.raises(MissingEventTypeError):
            await factory.CreateFromJson('["array", "json"]')
