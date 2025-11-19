from qdrant_client import QdrantClient

from MiravejaCore.Shared.DI import Container
from MiravejaCore.Shared.Embeddings.Domain.Configuration import EmbeddingConfig
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.VectorDatabase.Domain.Configuration import QdrantConfig
from MiravejaCore.Shared.VectorDatabase.Domain.Interfaces import IVectorDatabaseManagerFactory
from MiravejaCore.Shared.VectorDatabase.Infrastructure.Factories import QdrantVectorDatabaseManagerFactory
from MiravejaCore.Vector.Application.FindVectorById import FindVectorByIdHandler
from MiravejaCore.Vector.Application.GenerateImageVector import GenerateImageVectorHandler
from MiravejaCore.Vector.Application.GenerateTextVector import GenerateTextVectorHandler
from MiravejaCore.Vector.Application.MergeVectorsByIds import MergeVectorsHandler
from MiravejaCore.Vector.Application.SearchVectorsByText import SearchVectorsByTextHandler
from MiravejaCore.Vector.Application.UpdateVector import UpdateVectorHandler
from MiravejaCore.Vector.Domain.Interfaces import IEmbeddingProvider, IVectorRepository
from MiravejaCore.Vector.Domain.Services import VectorGenerationService
from MiravejaCore.Vector.Infrastructure.CLIP.Providers import ClipEmbeddingProvider
from MiravejaCore.Vector.Infrastructure.Qdrant.Repository import QdrantVectorRepository


class VectorDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        qdrantConfig: QdrantConfig = QdrantConfig.model_validate(container.Get("qdrantConfig"))

        container.RegisterFactories(
            {
                QdrantClient.__name__: lambda container: QdrantClient(
                    host=qdrantConfig.host,
                    port=qdrantConfig.port,
                    api_key=qdrantConfig.apiKey,
                    https=qdrantConfig.https,
                ),
                IVectorDatabaseManagerFactory.__name__: lambda container: QdrantVectorDatabaseManagerFactory(
                    resourceFactory=lambda: container.Get(QdrantClient.__name__),
                    config=qdrantConfig,
                ),
            }
        )

        container.RegisterFactories(
            {
                # Repositories
                IVectorRepository.__name__: lambda container: QdrantVectorRepository,
                # Providers
                IEmbeddingProvider.__name__: lambda container: ClipEmbeddingProvider(
                    config=EmbeddingConfig.model_validate(container.Get("embeddingConfig"))
                ),
                # Services
                VectorGenerationService.__name__: lambda container: VectorGenerationService(
                    embeddingProvider=container.Get(IEmbeddingProvider.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                # Handlers
                GenerateImageVectorHandler.__name__: lambda container: GenerateImageVectorHandler(
                    vectorGenerationService=container.Get(VectorGenerationService.__name__),
                    vectorDBFactory=container.Get(IVectorDatabaseManagerFactory.__name__),
                    tVectorRepository=container.Get(IVectorRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                ),
                GenerateTextVectorHandler.__name__: lambda container: GenerateTextVectorHandler(
                    vectorGenerationService=container.Get(VectorGenerationService.__name__),
                    vectorDBFactory=container.Get(IVectorDatabaseManagerFactory.__name__),
                    tVectorRepository=container.Get(IVectorRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                ),
                MergeVectorsHandler.__name__: lambda container: MergeVectorsHandler(
                    vectorDBFactory=container.Get(IVectorDatabaseManagerFactory.__name__),
                    tVectorRepository=container.Get(IVectorRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                ),
                UpdateVectorHandler.__name__: lambda container: UpdateVectorHandler(
                    vectorDBFactory=container.Get(IVectorDatabaseManagerFactory.__name__),
                    tVectorRepository=container.Get(IVectorRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                ),
                FindVectorByIdHandler.__name__: lambda container: FindVectorByIdHandler(
                    vectorDBFactory=container.Get(IVectorDatabaseManagerFactory.__name__),
                    tVectorRepository=container.Get(IVectorRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                SearchVectorsByTextHandler.__name__: lambda container: SearchVectorsByTextHandler(
                    vectorDBFactory=container.Get(IVectorDatabaseManagerFactory.__name__),
                    tVectorRepository=container.Get(IVectorRepository.__name__),
                    vectorGenerationService=container.Get(VectorGenerationService.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
