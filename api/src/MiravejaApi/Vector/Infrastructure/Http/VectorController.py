from MiravejaCore.Shared.Identifiers.Models import VectorId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse
from MiravejaCore.Vector.Application.FindVectorById import FindVectorByIdCommand, FindVectorByIdHandler
from MiravejaCore.Vector.Application.SearchVectorsByText import SearchVectorsByTextCommand, SearchVectorsByTextHandler


class VectorController:
    def __init__(
        self,
        findVectorByIdHandler: FindVectorByIdHandler,
        searchVectorsByTextHandler: SearchVectorsByTextHandler,
        logger: ILogger,
    ):
        self._findVectorByIdHandler = findVectorByIdHandler
        self._searchVectorsByTextHandler = searchVectorsByTextHandler
        self._logger = logger

    async def FindVectorById(self, vectorId: VectorId) -> HandlerResponse:
        command: FindVectorByIdCommand = FindVectorByIdCommand(vectorId=vectorId)
        vector = await self._findVectorByIdHandler.Handle(command)

        return vector

    async def SearchVectorsByText(self, command: SearchVectorsByTextCommand) -> HandlerResponse:
        vectors = await self._searchVectorsByTextHandler.Handle(command)

        return vectors
