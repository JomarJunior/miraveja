"""
Enum for image providers.
"""

from enum import Enum, IntEnum

class ProviderEnum(IntEnum):
    """
    Enumeration for image providers.
    """
    CIVIT_AI = 1

class ImageFormatEnum(str, Enum):
    PNG = "data:image/png"
    JPG = "data:image/jpeg"
    GIF = "data:image/gif"

    def to_extension(self) -> str:
        return self.value.split("/")[-1]
    
    @staticmethod
    def from_extension(extension: str) -> "ImageFormatEnum":
        mapping = {
            "png": ImageFormatEnum.PNG,
            "jpg": ImageFormatEnum.JPG,
            "jpeg": ImageFormatEnum.JPG,
            "gif": ImageFormatEnum.GIF,
        }
        result = mapping.get(extension.lower())
        if not result:
            raise ValueError(f"Unknown image extension: {extension}")
        return result
    
    def __str__(self):
        return self.value