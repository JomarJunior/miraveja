"""
Image acquisition interfaces.
"""

from src.Acquisition.Domain.Models import Image, ImageContent, Provider
from src.Acquisition.Domain.Enums import ProviderEnum
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

class IImageProvider(ABC):
    @abstractmethod
    def get_images(self, amount: int, cursor: str) -> List[Image]:
        """
        Retrieve a list of images based on the provided amount.
        """
        pass

    @abstractmethod
    def get_configuration_template(self) -> Dict:
        """
        Retrieve a template for the configuration parameters.
        """
        pass

class IProviderRepository(ABC):
    @abstractmethod
    def get_provider(self, provider: ProviderEnum) -> Provider:
        """
        Retrieve a specific image provider by its ID.
        """
        pass

class IImageDownloader(ABC):
    @abstractmethod
    def download_image(self, image: Image) -> ImageContent:
        """
        Download a specific image.
        """
        pass

class IStorageService(ABC):
    @abstractmethod
    def save_image_and_content(self, image: Image, content: ImageContent) -> Tuple[int, str]:
        """
        Save an image and its content, returning a tuple of (image_id, content_uri).
        """
        pass