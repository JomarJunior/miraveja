from abc import ABC, abstractmethod

from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Shared.Storage.Domain.Models import ImageContent


class IBucketService(ABC):
    def __init__(self, config: MinIoConfig):
        self.config = config
        self.bucketName = config.bucketName
        self.region = config.region

    @abstractmethod
    def EnsureBucketExists(self) -> None:
        pass


class IStorageService(ABC):
    @abstractmethod
    def UploadImage(self, imageContent: ImageContent) -> None:
        """Uploads an image to the storage."""

    @abstractmethod
    def DeleteImage(self, imageUri: str) -> None:
        """Deletes an image from the storage by its URI."""

    @abstractmethod
    def GetPresignedUrl(self, imageUri: str, expiresInSeconds: int) -> str:
        """Generates a presigned URL for accessing the image."""
