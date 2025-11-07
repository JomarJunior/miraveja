import json
from typing import Any, ClassVar, Dict, Generic, Optional, Tuple, Type, TypeVar
from pydantic import BaseModel, Field

import jsonschema

from MiravejaCore.Shared.Events.Domain.Exceptions import (
    EventAlreadyRegisteredError,
    EventNotFoundError,
    InvalidJsonStringError,
    MissingEventTypeError,
    MissingEventVersionError,
    SchemaValidationError,
)
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent, ISchemaRegistry
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Errors.Models import DomainException


class EventValidatorService:
    """Service responsible for validating events against their schemas."""

    def __init__(
        self,
        schemaRegistry: ISchemaRegistry,
        logger: ILogger,
    ):
        self._schemaRegistry = schemaRegistry
        self._logger = logger

    async def ValidateEvent(self, eventData: Dict[str, Any]) -> None:
        eventType: Optional[str] = eventData.get("type")
        if eventType is None:
            self._logger.Error("Event data missing 'type' field.")
            raise MissingEventTypeError()

        eventVersion: Optional[int] = eventData.get("version")
        if eventVersion is None:
            self._logger.Error("Event data missing 'version' field.")
            raise MissingEventVersionError()

        schema: Dict[str, Any] = await self._schemaRegistry.GetSchema(eventType, eventVersion)
        try:
            payload: Optional[Dict[str, Any]] = eventData.get("payload", None)
            if payload is None:
                self._logger.Error("Event data missing 'payload' field.")
                raise SchemaValidationError("Event data missing 'payload' field.")
            jsonschema.validate(instance=payload, schema=schema)  # We validate only the payload part of the event
            self._logger.Info(f"Event of type '{eventType}' and version '{eventVersion}' validated successfully.")
        except jsonschema.ValidationError as ve:
            self._logger.Error(f"Event validation failed: {ve.message}")
            raise SchemaValidationError(ve.message) from ve


class EventRegistry(BaseModel):
    """Registry for managing event types"""

    _eventRegistry: Dict[Tuple[str, int], Type[DomainEvent]] = {}
    logger: ILogger = None  # type: ignore

    model_config = {"arbitrary_types_allowed": True}

    def AttachLogger(self, logger: ILogger) -> None:
        """Attach a logger to the EventRegistry."""
        self.logger = logger
        self.logger.Info("Logger attached to EventRegistry.")
        self.logger.Debug(f"Current event registry keys: {list(self._eventRegistry.keys())}")

    def RegisterEvent(self, eventType: str, eventVersion: int):
        """Decorator to register a domain event class with its type and version."""

        def Decorator(eventClass: Type[DomainEvent]):
            key = (eventType, eventVersion)
            if self.logger:
                self.logger.Info(
                    f"Registering event: type='{eventType}', version='{eventVersion}', class='{eventClass.__name__}'"
                )
            if key in self._eventRegistry:
                raise EventAlreadyRegisteredError(eventType, eventVersion)
            self._eventRegistry[key] = eventClass
            return eventClass

        return Decorator

    def GetEventClass(self, eventType: str, eventVersion: int) -> Type[DomainEvent]:
        """Retrieve the domain event class for a given type and version."""
        key = (eventType, eventVersion)
        eventClass = self._eventRegistry.get(key)
        if eventClass is None:
            raise EventNotFoundError(eventType, eventVersion)
        return eventClass


eventRegistry: EventRegistry = EventRegistry()

T = TypeVar("T", bound=DomainEvent)


class EventDeserializerService(Generic[T]):
    """Service responsible for deserializing event data into domain event instances."""

    def __init__(
        self,
        _eventRegistry: EventRegistry,
        logger: ILogger,
    ):
        self._eventRegistry = _eventRegistry
        self._logger = logger

    def DeserializeEvent(self, eventData: Dict[str, Any]) -> T:
        eventType: Optional[str] = eventData.get("type")
        if eventType is None:
            self._logger.Error("Event data missing 'type' field.")
            raise MissingEventTypeError()

        eventVersion: Optional[int] = eventData.get("version")
        if eventVersion is None:
            self._logger.Error("Event data missing 'version' field.")
            raise MissingEventVersionError()

        payload: Optional[Dict[str, Any]] = eventData.get("payload", None)
        if payload is None:
            self._logger.Error("Event data missing 'payload' field.")
            raise SchemaValidationError("Event data missing 'payload' field.")

        eventClass: Type[DomainEvent] = self._eventRegistry.GetEventClass(eventType, eventVersion)
        eventInstance: T = eventClass.model_validate(payload)  # type: ignore
        self._logger.Info(f"Event of type '{eventType}' and version '{eventVersion}' deserialized successfully.")
        return eventInstance


@eventRegistry.RegisterEvent(eventType="event.exception.occurred", eventVersion=1)
class EventExceptionOccurred(DomainEvent):
    """Event representing an exception that occurred during event processing."""

    type: ClassVar[str] = "event.exception.occurred"
    aggregateType: str = "event"
    aggregateId: str = ""
    version: ClassVar[int] = 1
    exceptionMessage: str = Field(..., description="The exception message")
    exceptionCode: int = Field(..., description="The exception code")

    @classmethod
    def Create(
        cls,
        exceptionMessage: str,
        exceptionCode: str,
    ) -> "EventExceptionOccurred":
        """
        Create an EventExceptionOccurred.

        Args:
            aggregateId (str): The aggregate ID related to the event.
            exceptionMessage (str): The exception message.
            exceptionCode (str): The exception code.

        Returns:
            EventExceptionOccurred: The created event.
        """
        return cls(
            exceptionMessage=exceptionMessage,
            exceptionCode=exceptionCode,
        )


class EventFactory:
    """Factory for creating domain event instances from raw event data."""

    def __init__(
        self,
        deserializerService: EventDeserializerService,
        validatorService: EventValidatorService,
    ):
        self._deserializerService = deserializerService
        self._validatorService = validatorService

    async def CreateFromData(self, eventData: Dict[str, Any]) -> DomainEvent:
        await self._validatorService.ValidateEvent(eventData)
        return self._deserializerService.DeserializeEvent(eventData)

    async def CreateFromJson(self, eventJson: str) -> DomainEvent:
        try:
            eventData = json.loads(eventJson)
            return await self.CreateFromData(eventData)
        except json.JSONDecodeError as e:
            raise InvalidJsonStringError("Invalid JSON string provided for event creation.") from e

    async def CreateFromDomainException(self, exception: DomainException) -> EventExceptionOccurred:
        """Create a EventExceptionOccurred event from a DomainException."""

        event = EventExceptionOccurred.Create(
            exceptionMessage=exception.message,
            exceptionCode=exception.code,
        )
        return event
