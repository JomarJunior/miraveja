import os
from typing import Optional

from pydantic import BaseModel, Field


class QdrantConfig(BaseModel):
    """Configuration for Qdrant vector database."""

    host: str = Field(default="localhost", description="Qdrant server host")
    port: int = Field(default=6333, description="Qdrant server port")
    apiKey: Optional[str] = Field(default=None, description="Qdrant API key for authentication")
    https: bool = Field(default=False, description="Use HTTPS for Qdrant connection")
    collectionName: str = Field(default="image_embeddings", description="Default collection name for image embeddings")

    @classmethod
    def FromEnv(cls) -> "QdrantConfig":
        return cls(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", "6333")),
            apiKey=os.getenv("QDRANT_API_KEY"),
            https=os.getenv("QDRANT_HTTPS", "false").lower() in ("true", "1", "yes"),
            collectionName=os.getenv("QDRANT_COLLECTION_NAME", "image_embeddings"),
        )
