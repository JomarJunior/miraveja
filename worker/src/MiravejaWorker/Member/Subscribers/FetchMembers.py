from MiravejaCore.Member.Application.ListAllMembers import ListAllMembersCommand, ListAllMembersHandler
from MiravejaCore.Member.Domain.Events import FetchMembersEvent
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Events.Infrastructure.Kafka.Services import IEventSubscriber


class FetchMembersSubscriber(IEventSubscriber[FetchMembersEvent]):
    def __init__(
        self,
        logger: ILogger,
        listAllMembersHandler: ListAllMembersHandler,
    ):
        self._logger = logger
        self._listAllMembersHandler = listAllMembersHandler

    async def Handle(self, event: FetchMembersEvent) -> None:
        self._logger.Info(f"Handling FetchMembersEvent with ID: {event.id}")
        command: ListAllMembersCommand = ListAllMembersCommand.model_validate(
            event.model_dump(
                include=set(FetchMembersEvent.model_fields.keys()),
            )
        )
        await self._listAllMembersHandler.Handle(command)
        self._logger.Info(f"Completed handling FetchMembersEvent with ID: {event.id}")
