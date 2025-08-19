"""
Image provider implementation.
"""

from src.Acquisition.Domain.Interfaces import IImageProvider, IStorageService
from src.Acquisition.Domain.Models import Image, ImageContent, Provider
from src.Acquisition.Domain.Enums import ProviderEnum
from typing import Any, List, Dict
import requests

class CivitaiImageProvider(IImageProvider):
    def __init__(self, config: Dict):
        """
        Initialize the CivitaiImageProvider with the given configuration.
        """
        self.CIVIT_AI_QUERY_LIMIT = 200                                             # The maximum amount of images to fetch in a single request
        self.validate_configuration(config)
        self.api_url = config.get("provider_api_url")
        self.api_key = config.get("provider_api_key")
        self.model_version_id = config.get("provider_model_version_id")
        self.nsfw_level = config.get("provider_nsfw_level")
        self.sort_by = config.get("provider_sort_by")
        self.period = config.get("provider_period")
        self.skip_empty_metadata = config.get("provider_skip_empty_metadata")
        self.skip_videos = config.get("provider_skip_videos")
        self.force_download = config.get("provider_force_download")

    def get_images(self, amount: int = 200, cursor: str = "") -> List[Image]:
        """
        Get images from the Civitai API.
        """
        # Set up headers and parameters for the API request
        headers = self.build_api_headers()
        parameters_list = self.build_api_parameters(amount, cursor)

        images = []
        current_cursor = cursor
        for parameters in parameters_list:
            # Add the cursor
            parameters["cursor"] = current_cursor
            # Make the API request
            response = requests.get(f"{self.api_url}/images", headers=headers, params=parameters)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch images: {response.status_code} {response.text} \n Parameters: {parameters}")

            # Parse the response data
            data = response.json().get("items", [])

            # Update the cursor
            current_cursor = response.json().get("metadata", {}).get("nextCursor", "")

            # Validate and extract image data
            for item in data:
                print(item)
                image = Image.create(
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

    def build_api_parameters(self, limit: int, cursor: str) -> List[Dict[str, Any]]:
        """
        Build the parameters for the API request.
        Cursor format: <first_image_pointer>|<large_number>
        """
        parameters: List[Dict[str, Any]] = []
        while limit > 0:
            batch_size = min(limit, self.CIVIT_AI_QUERY_LIMIT)
            parameters.append({
                "sort": self.sort_by,
                "limit": batch_size,
                "period": self.period,
                "nsfw": self.nsfw_level,
            })
            limit -= batch_size

        return parameters

    def get_configuration_template(self) -> Dict:
        return {
            "provider_api_url": str,
            "provider_api_key": str,
            "provider_model_version_id": str,
            "provider_nsfw_level": str,
            "provider_sort_by": str,
            "provider_period": str,
            "provider_skip_empty_metadata": bool,
            "provider_skip_videos": bool,
            "provider_force_download": bool
        }

    def validate_configuration(self, config: Dict):
        template = self.get_configuration_template()
        for key, expected_type in template.items():
            if key not in config:
                raise ValueError(f"Missing configuration key: {key}")

            if expected_type == bool and not isinstance(config[key], expected_type):
                config[key] = config[key] == "True"

            if not isinstance(config[key], expected_type):
                raise ValueError(f"Invalid type for configuration key: {key}\nExpected: {expected_type}, Got: {type(config[key])}")
        return True
