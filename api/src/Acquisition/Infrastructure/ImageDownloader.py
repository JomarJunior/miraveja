"""
Image downloader implementation for various providers.
"""

from src.Acquisition.Domain.Interfaces import IImageDownloader, IStorageService
from src.Acquisition.Domain.Models import Image, ImageContent
from src.Acquisition.Domain.Enums import ImageFormatEnum
import requests
import base64
import time

class ImageDownloader(IImageDownloader):
    """
    Implementation of the image downloader interface for various providers.
    """
    def download_image(self, image: Image) -> ImageContent:
        """
        Download an image from the CivitAI provider.
        It expects the image metadata to contain a valid URL.
        It mutates the image object by setting the URI.
        """
        # Get the image URL from the metadata
        image_url = image.metadata.get("url")
        if not image_url:
            raise ValueError("Image metadata does not contain a valid URL")

        # Wait for a short period to avoid hitting the API rate limit
        time.sleep(0.1)

        # Download the image content
        response = requests.get(image_url)
        if response.status_code != 200:
            raise ValueError("Failed to download image")

        # Create the image content
        str_content: str = f"{self.get_image_format(image)};base64,{base64.b64encode(response.content).decode('utf-8')}"

        content = ImageContent.create(
            uri="",
            base64_content=str_content
        )

        # Return the created content
        return content

    def get_image_format(self, image: Image) -> ImageFormatEnum:
        """
        Get the image format from the image metadata.
        """
        image_url = image.metadata.get("url")
        if not image_url:
            raise ValueError("Image metadata does not contain a valid URL")

        return ImageFormatEnum.from_extension(image_url.split(".")[-1])
