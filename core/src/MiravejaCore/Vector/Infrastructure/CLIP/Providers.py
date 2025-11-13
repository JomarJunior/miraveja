import open_clip
import torch
from PIL.Image import Image
from torch import Tensor

from MiravejaCore.Shared.Embeddings.Domain.Configuration import EmbeddingConfig
from MiravejaCore.Vector.Domain.Interfaces import IEmbeddingProvider


class ClipEmbeddingProvider(IEmbeddingProvider):
    def __init__(self, config: EmbeddingConfig):
        self.model, self.preprocess = open_clip.create_model_from_pretrained(config.modelName)  # type: ignore
        self.model.eval()

    def _NormalizeEmbedding(self, embedding: Tensor) -> Tensor:
        return embedding / embedding.norm(dim=-1, keepdim=True)

    def _ConvertToFloatTensor(self, embedding: Tensor) -> Tensor:
        if embedding.dtype != torch.float32:
            embedding = embedding.float()
        return embedding

    async def GenerateImageEmbedding(self, image: Image) -> Tensor:
        processedImage = self.preprocess(image).unsqueeze(0)  # type: ignore # Add batch dimension
        with torch.no_grad(), torch.amp.autocast("cuda" if torch.cuda.is_available() else "cpu"):  # type: ignore
            embedding = self.model.encode_image(processedImage)  # type: ignore
            embedding = self._NormalizeEmbedding(embedding)  # Normalize
            embedding = self._ConvertToFloatTensor(embedding)  # Convert to float32
        return embedding.squeeze(0)  # Remove batch dimension

    async def GenerateTextEmbedding(self, text: str) -> Tensor:
        textTokens = open_clip.tokenize([text])  # type: ignore
        with torch.no_grad(), torch.amp.autocast("cuda" if torch.cuda.is_available() else "cpu"):  # type: ignore
            embedding = self.model.encode_text(textTokens)  # type: ignore
            embedding = self._NormalizeEmbedding(embedding)  # Normalize
            embedding = self._ConvertToFloatTensor(embedding)  # Convert to float32
        return embedding.squeeze(0)  # Remove batch dimension
