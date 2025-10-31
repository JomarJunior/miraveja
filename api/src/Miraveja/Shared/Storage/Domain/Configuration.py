import os
from urllib.parse import urlparse
from typing import List, Optional

from pydantic import BaseModel, Field
from Miraveja.Shared.Storage.Domain.Enums import MimeType, Region
from Miraveja.Shared.Storage.Domain.Models import SIZE_1_MB
from Miraveja.Shared.Utils.Constants.Binary import SIZE_128_MB
from Miraveja.Shared.Utils.Constants.Time import SECONDS_1_HOUR


class MinIoConfig(BaseModel):
    """Configuration for MinIO object storage using boto3."""

    endpoint: str = Field(default="http://localhost:9000", description="MinIO server endpoint URL")
    outsideEndpoint: str = Field(
        default="https://miraveja.127.0.0.1.nip.io/storage/", description="MinIO server outside endpoint URL"
    )
    accessKey: str = Field(default="minioadmin", description="MinIO access key")
    secretKey: str = Field(default="minioadmin", description="MinIO secret key")
    bucketName: str = Field(default="miraveja-bucket", description="Default bucket name")
    region: Optional[Region] = Field(default=None, description="Region name for the MinIO server")
    maxFileSizeBytes: int = Field(default=SIZE_128_MB, description="Maximum file size in bytes (default 100MB)")
    allowedMimeTypes: List[MimeType] = Field(
        default_factory=lambda: [MimeType.JPEG, MimeType.PNG, MimeType.GIF],
        description="List of allowed MIME types for file uploads",
    )
    presignedUrlExpirationSeconds: int = Field(
        default=SECONDS_1_HOUR, description="Expiration time in seconds for presigned URLs (default 1 hour)"
    )

    @property
    def maxFileSizeMB(self) -> float:
        return self.maxFileSizeBytes / (SIZE_1_MB)

    @property
    def endpointUrl(self) -> str:
        parsedUrl = urlparse(self.endpoint)
        return f"{parsedUrl.scheme}://{parsedUrl.netloc}"

    @classmethod
    def FromEnv(cls) -> "MinIoConfig":
        return cls(
            endpoint=os.getenv("MINIO_ENDPOINT", "http://localhost:9000"),
            outsideEndpoint=os.getenv("MINIO_OUTSIDE_ENDPOINT", "https://miraveja.127.0.0.1.nip.io/storage/"),
            accessKey=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
            secretKey=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
            bucketName=os.getenv("MINIO_BUCKET_NAME", "miraveja-bucket"),
            region=Region(os.getenv("MINIO_REGION")) if os.getenv("MINIO_REGION") else None,
            maxFileSizeBytes=int(os.getenv("MINIO_MAX_FILE_SIZE", str(SIZE_128_MB))),
            allowedMimeTypes=[
                MimeType(mime)
                for mime in os.getenv("MINIO_ALLOWED_MIME_TYPES", "image/jpeg,image/png,image/gif").split(",")
            ],
            presignedUrlExpirationSeconds=int(os.getenv("MINIO_PRESIGNED_URL_EXPIRATION_SECONDS", "3600")),
        )
