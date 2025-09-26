"""
Model for the Processing context
"""

from src.Core.Events.Bus import EventEmitter
from src.Processing.Domain.Enums import DistanceMetricEnum
from src.Processing.Domain.Events import (
    ImageEmbeddingCreatedEvent,
    TextEmbeddingCreatedEvent,
    ImageThumbnailCreatedEvent
)
from torch import Tensor
from typing import Any, Dict
import base64

class Embedding:
    """
    Base class for all embeddings.
    """
    def __init__(self, tensor: Tensor):
        self.tensor = tensor

    @classmethod
    def from_tensor(cls, tensor: Tensor) -> "Embedding":
        return cls(tensor)
    
    def to_tensor(self) -> Tensor:
        return self.tensor
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Embedding):
            return False
        return self.tensor.equal(other.tensor)

    def distance_to(self, other: "Embedding", metric: DistanceMetricEnum = DistanceMetricEnum.EUCLIDEAN) -> float:
        if not isinstance(other, Embedding):
            raise TypeError("Distance can only be calculated between Embedding instances.")

        if metric == DistanceMetricEnum.EUCLIDEAN:
            return (self.tensor - other.tensor).norm().item()
        elif metric == DistanceMetricEnum.COSINE:
            return 1 - (self.tensor @ other.tensor) / (self.tensor.norm() * other.tensor.norm())
        else:
            raise ValueError(f"Unknown distance metric: {metric}")

    def __repr__(self) -> str:
        return f"Embedding(tensor_shape={self.tensor.shape})"

class ImageEmbedding(EventEmitter):
    """
    Relationship between an image and its embedding representation.
    """
    def __init__(self, image_id: int, embedding: Embedding):
        super().__init__()
        self.image_id = image_id
        self.embedding = embedding

    @classmethod
    def create(cls, image_id: int, embedding: Tensor) -> "ImageEmbedding":
        """
        Factory method to create an ImageEmbedding instance.
        """
        image_embedding = cls(image_id, Embedding.from_tensor(embedding))
        image_embedding.emit_event(ImageEmbeddingCreatedEvent(image_embedding))
        return image_embedding
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageEmbedding":
        """
        Factory method to create an ImageEmbedding instance from a dictionary.
        """
        image_id = data.get("image_id")
        embedding = data.get("embedding")

        if not image_id:
            raise ValueError("Cannot create ImageEmbedding without image_id")
        if not embedding:
            raise ValueError("Cannot create ImageEmbedding without embedding")

        return cls(image_id, Embedding.from_tensor(Tensor(embedding)))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ImageEmbedding instance to a dictionary.
        """
        return {
            "image_id": self.image_id,
            "embedding": self.embedding.to_tensor().tolist(),  # Convert tensor to list for serialization
        }
    
    def __repr__(self) -> str:
        return f"ImageEmbedding(image_id={self.image_id}, embedding={self.embedding})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageEmbedding):
            return False
        return self.image_id == other.image_id and self.embedding == other.embedding

class TextEmbedding(EventEmitter):
    """
    Relationship between a text and its embedding representation.
    """
    def __init__(self, text: str, embedding: Embedding):
        super().__init__()
        self.text = text
        self.embedding = embedding

    @classmethod
    def create(cls, text: str, embedding: Tensor) -> "TextEmbedding":
        """
        Factory method to create a TextEmbedding instance.
        """
        text_embedding = cls(text, Embedding.from_tensor(embedding))
        text_embedding.emit_event(TextEmbeddingCreatedEvent(text_embedding))
        return text_embedding

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TextEmbedding":
        """
        Factory method to create a TextEmbedding instance from a dictionary.
        """
        text = data.get("text")
        embedding = data.get("embedding")

        if not text:
            raise ValueError("Cannot create TextEmbedding without text")
        if not embedding:
            raise ValueError("Cannot create TextEmbedding without embedding")

        return cls(text, Embedding.from_tensor(Tensor(embedding)))

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the TextEmbedding instance to a dictionary.
        """
        return {
            "text": self.text,
            "embedding": self.embedding.to_tensor().tolist(),  # Convert tensor to list for serialization
        }

    def __repr__(self) -> str:
        return f"TextEmbedding(text={self.text}, embedding={self.embedding})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TextEmbedding):
            return False
        return self.text == other.text and self.embedding == other.embedding
    
class ImageThumbnail(EventEmitter):
    """
    Relationship between an image and its thumbnail base64 representation.
    """
    def __init__(self, image_id: int, thumbnail_base64: str):
        super().__init__()
        self.image_id = image_id
        self.thumbnail_base64 = thumbnail_base64

    @classmethod
    def create(cls, image_id: int, thumbnail_base64: str) -> "ImageThumbnail":
        """
        Factory method to create an ImageThumbnail instance.
        """
        image_thumbnail = cls(image_id, thumbnail_base64)
        image_thumbnail.emit_event(ImageThumbnailCreatedEvent(image_thumbnail))
        return image_thumbnail
    
    @classmethod
    def create_from_bytes(cls, image_id: int, image_bytes: bytes) -> "ImageThumbnail":
        """
        Factory method to create an ImageThumbnail instance from image bytes.
        """
        thumbnail_base64 = base64.b64encode(image_bytes).decode("utf-8")
        image_thumbnail = cls(image_id, thumbnail_base64)
        image_thumbnail.emit_event(ImageThumbnailCreatedEvent(image_thumbnail))
        return image_thumbnail

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageThumbnail":
        """
        Factory method to create an ImageThumbnail instance from a dictionary.
        """
        image_id = data.get("image_id")
        thumbnail_base64 = data.get("thumbnail_base64")

        if not image_id:
            raise ValueError("Cannot create ImageThumbnail without image_id")
        if not thumbnail_base64:
            raise ValueError("Cannot create ImageThumbnail without thumbnail_base64")

        return cls(image_id, thumbnail_base64)
    
    def to_bytes(self) -> bytes:
        """
        Convert the ImageThumbnail instance to bytes.
        """
        return base64.b64decode(self.thumbnail_base64)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the ImageThumbnail instance to a dictionary.
        """
        return {
            "image_id": self.image_id,
            "thumbnail_base64": self.thumbnail_base64,
        }

    def __repr__(self) -> str:
        return f"ImageThumbnail(image_id={self.image_id}, thumbnail_base64_length={len(self.thumbnail_base64)})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageThumbnail):
            return False
        return self.image_id == other.image_id and self.thumbnail_base64 == other.thumbnail_base64