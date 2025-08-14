"""
Image downloader implementation for various providers.
"""

from src.Acquisition.Domain.Interfaces import IImageDownloader, IImageContentRepository
from src.Acquisition.Domain.Models import Image, ImageContent
import requests
import base64

class ImageDownloader(IImageDownloader):
    """
    Implementation of the image downloader interface for various providers.
    """
    def __init__(self, content_repository: IImageContentRepository):
        self.content_repository = content_repository


    def download_image(self, image: Image) -> ImageContent:
        """
        Download an image from the CivitAI provider.
        It expects the image metadata to contain a valid URL.
        It mutates the image object by setting the URI.
        """
        # Get the content URI for the image
        content_uri = self.content_repository.get_path_for_image(image.id)
        image.uri = content_uri

        # Get the image URL from the metadata
        image_url = image.metadata.get("url")
        if not image_url:
            raise ValueError("Image metadata does not contain a valid URL")

        # Download the image content
        response = requests.get(image_url)
        if response.status_code != 200:
            raise ValueError("Failed to download image")

        # Create the image content
        content = ImageContent.create(
            uri=content_uri,
            base64_content=base64.b64encode(response.content).decode("utf-8")
        )

        # Return the created content
        return content