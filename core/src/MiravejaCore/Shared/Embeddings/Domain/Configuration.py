import os

from pydantic import BaseModel, Field


class EmbeddingConfig(BaseModel):
    """Configuration for embedding models."""

    modelName: str = Field(
        default="hf-hub:laion/CLIP-ViT-g-14-laion2B-s12B-b42K",
        description="Name of the embedding model to use.",
    )

    @classmethod
    def FromEnv(cls) -> "EmbeddingConfig":
        config = cls()
        modelName = os.getenv("EMBEDDING_MODEL_NAME")
        if modelName:
            config.modelName = modelName

        return config
