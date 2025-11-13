from enum import Enum


class VectorType(str, Enum):
    IMAGE = "image"
    TEXT = "text"

    def __str__(self) -> str:
        return self.value
