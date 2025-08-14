"""
Interfaces for Storage context
"""

from src.Storage.Domain.Models import Image, Provider, ImageContent
from abc import ABC, abstractmethod
from typing import List

class IImageRepository(ABC):
    @abstractmethod
    def list_all(self, sort_by: str, sort_order: str, search_filter: dict, limit: int) -> List[Image]:
        pass

    @abstractmethod
    def find_by_id(self, image_id: int) -> Image:
        pass

    @abstractmethod
    def save(self, image: Image) -> None:
        pass

class IProviderRepository(ABC):
    @abstractmethod
    def list_all(self, sort_by: str, sort_order: str, search_filter: dict, limit: int) -> List[Provider]:
        pass

    @abstractmethod
    def find_by_id(self, provider_id: int) -> Provider:
        pass

    @abstractmethod
    def save(self, provider: Provider) -> None:
        pass

class IImageContentRepository(ABC):
    @abstractmethod
    def find_by_uri(self, uri: str) -> ImageContent:
        pass

    @abstractmethod
    def save(self, image_content: ImageContent) -> None:
        pass

    @abstractmethod
    def get_next_available_uri(self, extension: str) -> str:
        pass

class IEncryptionService(ABC):
    @abstractmethod
    def encrypt(self, data: str) -> bytes:
        pass

    @abstractmethod
    def decrypt(self, data: bytes) -> str:
        pass