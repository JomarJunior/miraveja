import json
from typing import Any, Dict, Generic, Optional, Tuple, Type, TypeVar

import jsonschema

from MiravejaCore.Shared.Events.Domain.Exceptions import (
    EventAlreadyRegisteredError,
    EventNotFoundError,
    MissingEventTypeError,
    MissingEventVersionError,
    SchemaValidationError,
)
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent, ISchemaRegistry
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from pydantic import BaseModel


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
        eventType: Optional[str] = eventData.get("eventType")
        if eventType is None:
            self._logger.Error("Event data missing 'eventType' field.")
            raise MissingEventTypeError()

        eventVersion: Optional[int] = eventData.get("version")
        if eventVersion is None:
            self._logger.Error("Event data missing 'eventVersion' field.")
            raise MissingEventVersionError()

        schema: Dict[str, Any] = await self._schemaRegistry.GetSchema(eventType, eventVersion)
        try:
            jsonschema.validate(instance=eventData, schema=schema)
            self._logger.Info(f"Event of type '{eventType}' and version '{eventVersion}' validated successfully.")
        except jsonschema.ValidationError as ve:
            self._logger.Error(f"Event validation failed: {ve.message}")
            raise SchemaValidationError(ve.message) from ve


class EventRegistry(BaseModel):
    """Registry for managing event types"""

    _eventRegistry: Dict[Tuple[str, int], Type[DomainEvent]] = {}

    def RegisterEvent(self, eventType: str, eventVersion: int):
        """Decorator to register a domain event class with its type and version."""

        def Decorator(eventClass: Type[DomainEvent]):
            key = (eventType, eventVersion)
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


eventRegistry = EventRegistry()

T = TypeVar("T", bound=DomainEvent)


class EventDeserializerService(Generic[T]):
    """Service responsible for deserializing event data into domain event instances."""

    def __init__(
        self,
        eventRegistry: EventRegistry,
        logger: ILogger,
    ):
        self._eventRegistry = eventRegistry
        self._logger = logger

    def DeserializeEvent(self, eventData: Dict[str, Any]) -> T:
        eventType: Optional[str] = eventData.get("eventType")
        if eventType is None:
            self._logger.Error("Event data missing 'eventType' field.")
            raise MissingEventTypeError()

        eventVersion: Optional[int] = eventData.get("version")
        if eventVersion is None:
            self._logger.Error("Event data missing 'eventVersion' field.")
            raise MissingEventVersionError()

        eventClass: Type[DomainEvent] = self._eventRegistry.GetEventClass(eventType, eventVersion)
        eventInstance: T = eventClass.model_validate(eventData)  # type: ignore
        self._logger.Info(f"Event of type '{eventType}' and version '{eventVersion}' deserialized successfully.")
        return eventInstance


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
        eventData = json.loads(eventJson)
        return await self.CreateFromData(eventData)
