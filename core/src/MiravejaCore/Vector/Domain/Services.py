from io import BytesIO

from PIL import Image
from torch import Tensor

from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Vector.Domain.Interfaces import IEmbeddingProvider


class VectorGenerationService:
    def __init__(
        self,
        embeddingProvider: IEmbeddingProvider,
        logger: ILogger,
    ):
        self.embeddingProvider = embeddingProvider
        self.logger = logger

    async def ProcessImage(self, imageData: BytesIO) -> Image.Image:
        image = Image.open(imageData)
        return image.convert("RGB")  # Ensure image is in RGB format

    async def ProcessEmbedding(self, embedding: Tensor) -> Tensor:
        processed = embedding / embedding.norm()  # Normalize embedding
        return processed

    async def GenerateTextVector(self, text: str) -> Tensor:
        self.logger.Info("Generating text embedding.")
        embedding = await self.embeddingProvider.GenerateTextEmbedding(text)
        self.logger.Info("Text embedding generated.")
        return await self.ProcessEmbedding(embedding)

    async def GenerateImageVector(self, imageData: BytesIO) -> Tensor:
        self.logger.Info("Generating image embedding.")
        image = await self.ProcessImage(imageData)
        embedding = await self.embeddingProvider.GenerateImageEmbedding(image)
        self.logger.Info("Image embedding generated.")
        return await self.ProcessEmbedding(embedding)
