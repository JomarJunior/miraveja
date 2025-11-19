import open_clip
import torch
from PIL.Image import Image
from torch import Tensor

from MiravejaCore.Shared.Embeddings.Domain.Configuration import EmbeddingConfig
from MiravejaCore.Vector.Domain.Interfaces import IEmbeddingProvider


class ClipEmbeddingProvider(IEmbeddingProvider):
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.model = None
        self.preprocess = None

    def _InitializeModel(self):
        if self.model is not None and self.preprocess is not None:
            return

        self.model, self.preprocess = open_clip.create_model_from_pretrained(
            self.config.modelName, pretrained=self.config.pretrained, cache_dir=self.config.cacheDir
        )  # type: ignore
        self.model.eval()

    def _NormalizeEmbedding(self, embedding: Tensor) -> Tensor:
        return embedding / embedding.norm(dim=-1, keepdim=True)

    def _ConvertToFloatTensor(self, embedding: Tensor) -> Tensor:
        if embedding.dtype != torch.float32:
            embedding = embedding.float()
        return embedding

    async def GenerateImageEmbedding(self, image: Image) -> Tensor:
        self._InitializeModel()
        processedImage = self.preprocess(image).unsqueeze(0)  # type: ignore # Add batch dimension
        with torch.no_grad(), torch.amp.autocast("cuda" if torch.cuda.is_available() else "cpu"):  # type: ignore
            embedding = self.model.encode_image(processedImage)  # type: ignore
            embedding = self._NormalizeEmbedding(embedding)  # Normalize
            embedding = self._ConvertToFloatTensor(embedding)  # Convert to float32
        return embedding.squeeze(0)  # Remove batch dimension

    async def GenerateTextEmbedding(self, text: str) -> Tensor:
        self._InitializeModel()
        textTokens = open_clip.tokenize([text])  # type: ignore
        with torch.no_grad(), torch.amp.autocast("cuda" if torch.cuda.is_available() else "cpu"):  # type: ignore
            embedding = self.model.encode_text(textTokens)  # type: ignore
            embedding = self._NormalizeEmbedding(embedding)  # Normalize
            embedding = self._ConvertToFloatTensor(embedding)  # Convert to float32
        return embedding.squeeze(0)  # Remove batch dimension
