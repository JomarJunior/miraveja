"""
Image provider implementation.
"""

from src.Acquisition.Domain.Interfaces import IImageProvider, IImageContentRepository
from src.Acquisition.Domain.Models import Image, ImageContent, Provider
from src.Acquisition.Domain.Enums import ProviderEnum
from typing import List, Dict
import requests

class CivitaiImageProvider(IImageProvider):
    def __init__(self, config: Dict, content_repository: IImageContentRepository):
        """
        Initialize the CivitaiImageProvider with the given configuration.
        """
        self.validate_configuration(config)
        self.api_url = config.get("api_url")
        self.api_key = config.get("api_key")
        self.model_version_id = config.get("model_version_id")
        self.nsfw_level = config.get("nsfw_level")
        self.sort_by = config.get("sort_by")
        self.period = config.get("period")
        self.skip_empty_metadata = config.get("skip_empty_metadata")
        self.skip_videos = config.get("skip_videos")
        self.force_download = config.get("force_download")
        self.content_repository = content_repository

    def get_images(self, amount: int) -> List[Image]:
        """
        Get images from the Civitai API.
        """
        # Set up headers and parameters for the API request
        headers = self.build_api_headers()
        parameters = self.build_api_parameters()
        # Set the limit for the number of images to retrieve
        parameters["limit"] = amount

        # Make the API request
        response = requests.get(f"{self.api_url}/images", headers=headers, params=parameters)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch images: {response.status_code} {response.text}")

        # Parse the response data
        data = response.json()

        # Validate and extract image data
        images = []
        for item in data:
            image = Image.create(
                id=item["id"],
                uri="",
                metadata=item,
                provider_id=ProviderEnum.CIVIT_AI
            )
            images.append(image)

        # Return the list of images
        return images

    def build_api_headers(self) -> Dict:
        """
        Build the headers for the API request.
        """
        return {
            "Authorization": f"Bearer {self.api_key}"
        }

    def build_api_parameters(self) -> Dict:
        """
        Build the parameters for the API request.
        """
        return {
            "sort": self.sort_by,
            "period": self.period,
            "nsfw": self.nsfw_level
        }

    def get_configuration_template(self) -> Dict:
        return {
            "api_url": str,
            "api_key": str,
            "model_version_id": str,
            "nsfw_level": str,
            "sort_by": str,
            "period": str,
            "skip_empty_metadata": bool,
            "skip_videos": bool,
            "force_download": bool
        }

    def validate_configuration(self, config: Dict):
        template = self.get_configuration_template()
        for key, expected_type in template.items():
            if key not in config:
                raise ValueError(f"Missing configuration key: {key}")
            if not isinstance(config[key], expected_type):
                raise ValueError(f"Invalid type for configuration key: {key}")
        return True
