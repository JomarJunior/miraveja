"""
Interfaces for the Processing domain.
"""

from src.Processing.Domain.Models import Embedding, ImageEmbedding, TextEmbedding, ImageThumbnail
from src.Processing.Domain.Enums import DistanceMetricEnum
from abc import ABC, abstractmethod

class IEmbeddingsGenerationService(ABC):
    """
    Interface for embedding generation services.
    """
    @abstractmethod
    def generate_image_embedding(self, image_id: int) -> ImageEmbedding:
        pass

    @abstractmethod
    def generate_text_embedding(self, text: str) -> TextEmbedding:
        pass

class IEmbeddingsCalculationService(ABC):
    """
    Interface for embedding calculation services.
    """
    @abstractmethod
    def calculate_similarity(self, first_embedding: Embedding, second_embedding: Embedding, metric: DistanceMetricEnum) -> float:
        """
        This method calculates the similarity between two embeddings using the specified distance metric.
        """
        pass

    @abstractmethod
    def calculate_distance(self, first_embedding: Embedding, second_embedding: Embedding, metric: DistanceMetricEnum) -> float:
        """
        This method calculates the distance between two embeddings using the specified distance metric.
        """
        pass

class IThumbnailService(ABC):
    """
    Interface for thumbnail generation services.
    """
    @abstractmethod
    def generate_image_thumbnail(self, image_id: int) -> ImageThumbnail:
        pass

class IStorageService(ABC):
    """
    Interface for storage services.
    """
    @abstractmethod
    def save_image_embedding(self, image_embedding: ImageEmbedding) -> None:
        pass

    @abstractmethod
    def find_image_embedding(self, image_id: int) -> ImageEmbedding:
        pass

    @abstractmethod
    def save_text_embedding(self, text_embedding: TextEmbedding) -> None:
        pass

    @abstractmethod
    def find_text_embedding(self, text: str) -> TextEmbedding:
        pass

    @abstractmethod
    def save_image_thumbnail(self, image_thumbnail: ImageThumbnail) -> None:
        pass

    @abstractmethod
    def find_image_thumbnail(self, image_id: int) -> ImageThumbnail:
        pass

    @abstractmethod
    def retrieve_image_content_by_id(self, image_id: int) -> str:
        pass