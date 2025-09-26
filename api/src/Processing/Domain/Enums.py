"""
Enums for the Processing domain
"""

from enum import Enum

class DistanceMetricEnum(str, Enum):
    EUCLIDEAN = "euclidean"
    COSINE = "cosine"

class ImageExtensionEnum(str, Enum):
    JPG = "jpg"
    PNG = "png"
    GIF = "gif"

    def to_base64_prefix(self) -> str:
        return f"data:image/{self.value};base64,"