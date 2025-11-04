from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent, IEventProducer
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class EventDispatcher:
    def __init__(self, eventProducer: IEventProducer, logger: ILogger):
        self._eventProducer = eventProducer
        self._logger = logger

    async def DispatchAll(self, events: list[DomainEvent]) -> None:
        """Dispatch all given domain events using the event producer."""
        if not events:
            self._logger.Info("No events to dispatch.")
            return

        self._logger.Info(f"Dispatching {len(events)} events.")
        try:
            await self._eventProducer.ProduceAll(events)
            self._logger.Info("All events dispatched successfully.")
        except Exception as ex:
            self._logger.Error(f"Failed to dispatch events: {ex}")
            raise ex

    async def Dispatch(self, event: DomainEvent) -> None:
        """Dispatch a single domain event using the event producer."""
        if event is None:
            self._logger.Warning("No event to dispatch.")
            return

        self._logger.Info(f"Dispatching event: {event}")
        try:
            await self._eventProducer.Produce(event)
            self._logger.Info("Event dispatched successfully.")
        except Exception as ex:
            self._logger.Error(f"Failed to dispatch event: {ex}")
            raise ex
