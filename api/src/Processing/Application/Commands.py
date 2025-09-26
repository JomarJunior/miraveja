from pydantic import BaseModel, Field, field_validator
from typing import Optional

"""
Handlers commands for image processing.
"""
class GetTextEmbeddingCommand(BaseModel):
    text: str = Field(..., min_length=1, description="Text to generate embedding for")
    detached: bool = Field(default=False, description="Whether to run detached")

    @field_validator('text')
    def validate_text(cls, v):
        if not v or not v.strip():
            raise ValueError("Invalid text")
        return v
    
    @classmethod
    def from_dict(cls, data: dict) -> "GetTextEmbeddingCommand":
        text: str = data["text"]
        detached: bool = data.get("detached", False)

        return cls(text=text, detached=detached)


class GetImageEmbeddingCommand(BaseModel):
    image_id: int = Field(..., gt=0, description="Image ID to generate embedding for")
    detached: bool = Field(default=False, description="Whether to run detached")

    @field_validator('image_id')
    def validate_image_id(cls, v):
        if not v:
            raise ValueError("Cannot generate embedding for image without ID")
        return v

    @classmethod
    def from_dict(cls, data: dict) -> "GetImageEmbeddingCommand":
        image_id: int = data["image_id"]
        detached: bool = data.get("detached", False)

        return cls(image_id=image_id, detached=detached)


class GetImageThumbnailCommand(BaseModel):
    image_id: int = Field(..., gt=0, description="Image ID to generate thumbnail for")
    detached: bool = Field(default=False, description="Whether to run detached")

    @field_validator('image_id')
    def validate_image_id(cls, v):
        if not v:
            raise ValueError("Cannot generate thumbnail for image without ID")
        return v

    @classmethod
    def from_dict(cls, data: dict) -> "GetImageThumbnailCommand":
        image_id: int = data["image_id"]
        detached: bool = data.get("detached", False)

        if not image_id:
            raise ValueError("Cannot generate thumbnail for image without ID")

        return cls(image_id=image_id, detached=detached)