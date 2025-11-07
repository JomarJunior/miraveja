from fastapi import HTTPException

from MiravejaCore.Member.Application.ListAllMembers import ILogger
from MiravejaCore.Member.Domain.Exceptions import DomainException
from MiravejaApi.Events.Application.ConnectStream import ConnectStreamCommand, ConnectStreamHandler


class EventsController:
    def __init__(
        self,
        connectStreamHandler: ConnectStreamHandler,
        logger: ILogger,
    ):
        self._connectStreamHandler = connectStreamHandler
        self._logger = logger

    async def ConnectStream(self, command: ConnectStreamCommand) -> None:
        try:
            await self._connectStreamHandler.Handle(command)
        except DomainException as domainException:
            self._logger.Error(f"{str(domainException)}")
            raise HTTPException(status_code=400, detail=str(domainException)) from domainException
        except Exception as exception:
            self._logger.Error(f"Unexpected error during connecting event stream: {str(exception)}")
            raise HTTPException(status_code=500, detail="Internal server error") from exception
