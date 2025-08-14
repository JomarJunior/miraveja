"""
Image acquisition interfaces.
"""

from src.Acquisition.Domain.Models import Image, ImageContent, Provider
from src.Acquisition.Domain.Enums import ProviderEnum
from abc import ABC, abstractmethod
from typing import List, Dict

class IImageProvider(ABC):
    @abstractmethod
    def get_images(self, amount: int) -> List[Image]:
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

class IImageRepository(ABC):
    @abstractmethod
    def save_image(self, image: Image):
        """
        Save an image.
        """
        pass

    @abstractmethod
    def get_next_available_id(self) -> str:
        """
        Get the next available ID for a new image.
        """
        pass

class IImageContentRepository(ABC):
    @abstractmethod
    def save_image_content(self, content: ImageContent) -> str:
        """
        Save image content and return the path to the saved content.
        """
        pass

    @abstractmethod
    def get_path_for_image(self, image_id: int) -> str:
        """
        Get the file path for a specific image.
        """
        pass