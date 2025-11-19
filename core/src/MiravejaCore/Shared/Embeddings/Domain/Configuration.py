import os

from pydantic import BaseModel, Field


class EmbeddingConfig(BaseModel):
    """Configuration for embedding models."""

    modelName: str = Field(
        default="ViT-g-14",
        description="Name of the embedding model to use.",
    )
    pretrained: str = Field(
        default="laion2b_s12b_b42k",
        description="Pretrained model to use.",
    )
    cacheDir: str = Field(
        default="/models",
        description="Directory to cache the models.",
    )

    @classmethod
    def FromEnv(cls) -> "EmbeddingConfig":
        config = cls()
        modelName = os.getenv("EMBEDDING_MODEL_NAME")
        if modelName:
            config.modelName = modelName

        pretrained = os.getenv("EMBEDDING_PRETRAINED")
        if pretrained:
            config.pretrained = pretrained

        cacheDir = os.getenv("EMBEDDING_CACHE_DIR")
        if cacheDir:
            config.cacheDir = cacheDir

        return config
