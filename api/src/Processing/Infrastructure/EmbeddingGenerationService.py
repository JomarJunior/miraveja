"""
Implements the embedding generation service.
"""

from io import BytesIO
from src.Processing.Domain.Interfaces import IEmbeddingsGenerationService, IStorageService
from src.Processing.Domain.Models import ImageEmbedding, TextEmbedding
from PIL import Image
import torch
from torch import Tensor
from transformers import CLIPProcessor, CLIPModel
from typing import Optional
import base64


class ClipEmbeddingsGenerationService(IEmbeddingsGenerationService):
    """
    Implements the embedding generation service using CLIP.
    CLIP is a neural network architecture that learns visual concepts from natural language descriptions.
    """
    def __init__(
            self,
            storage_service: IStorageService,
            model_name: str = "openai/clip-vit-base-patch32",
            device: Optional[str] = None
    ):
        self.storage_service: IStorageService = storage_service
        self.device: str = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name: str = model_name
        self.model: CLIPModel = CLIPModel.from_pretrained(model_name)
        self.processor: CLIPProcessor = CLIPProcessor.from_pretrained(model_name, use_fast=True)

    def generate_image_embedding(self, image_id: int) -> ImageEmbedding:
        # Retrieve image from storage
        image_data: str = self.storage_service.retrieve_image_content_by_id(image_id)
        decoded_image_data = base64.b64decode(image_data)

        # Load image
        image_buffer: BytesIO = BytesIO(decoded_image_data)
        image: Image.Image = Image.open(image_buffer)

        # Ensure image is in RGB format
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Preprocess image
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        image_features: Tensor = self.model.get_image_features(**inputs) # type: ignore

        # Create image embedding
        image_embedding = ImageEmbedding.create(image_id=image_id, embedding=image_features.cpu())
        return image_embedding
    
    def generate_text_embedding(self, text: str) -> TextEmbedding:
        # Preprocess text
        inputs = self.processor(text=text, return_tensors="pt").to(self.device)

        # Generate text features
        text_features: Tensor = self.model.get_text_features(**inputs) # type: ignore

        # Create text embedding
        text_embedding = TextEmbedding.create(text=text, embedding=text_features.cpu())
        return text_embedding