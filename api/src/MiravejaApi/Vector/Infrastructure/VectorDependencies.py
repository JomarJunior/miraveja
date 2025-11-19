from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Vector.Application.SearchVectorsByText import SearchVectorsByTextHandler
from MiravejaCore.Vector.Infrastructure.VectorDependencies import VectorDependencies as VectorDependenciesBase

from MiravejaApi.Vector.Infrastructure.Http.VectorController import FindVectorByIdHandler, VectorController


class VectorDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        VectorDependenciesBase.RegisterDependencies(container)
        container.RegisterFactories(
            {
                # Controllers
                VectorController.__name__: lambda container: VectorController(
                    findVectorByIdHandler=container.Get(FindVectorByIdHandler.__name__),
                    searchVectorsByTextHandler=container.Get(SearchVectorsByTextHandler.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
