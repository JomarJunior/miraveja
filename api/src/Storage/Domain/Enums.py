"""
Enums for Storage Context
"""

from enum import Enum

class ImageFormatEnum(str, Enum):
    PNG = "data:image/png"
    JPG = "data:image/jpeg"
    GIF = "data:image/gif"

    def to_extension(self) -> str:
        return self.value.split("/")[-1]
    
    def to_mime_type(self) -> str:
        return self.value.split(":")[1]