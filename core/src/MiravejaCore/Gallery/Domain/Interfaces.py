from abc import ABC, abstractmethod
from typing import Any, BinaryIO, Dict, Iterator, Optional

from MiravejaCore.Gallery.Domain.Models import GenerationMetadata, ImageMetadata, LoraMetadata, Size
from MiravejaCore.Shared.Identifiers.Models import GenerationMetadataId, ImageMetadataId, LoraMetadataId, MemberId
from MiravejaCore.Shared.Storage.Domain.Enums import MimeType
from MiravejaCore.Shared.Utils.Repository.Queries import ListAllQuery
from MiravejaCore.Shared.Utils.Repository.Types import FilterFunction


class IImageMetadataRepository(ABC):
    """Interface for image metadata repository."""

    @abstractmethod
    def ListAll(
        self,
        query: ListAllQuery = ListAllQuery(),
        filterFunction: Optional[FilterFunction] = None,
    ) -> Iterator[ImageMetadata]:
        pass

    @abstractmethod
    def Count(self) -> int:
        pass

    @abstractmethod
    def FindById(self, imageId: ImageMetadataId) -> Optional[ImageMetadata]:
        pass

    @abstractmethod
    def FindByUri(self, uri: str) -> Optional[ImageMetadata]:
        pass

    @abstractmethod
    def ImageMetadataExists(self, imageId: ImageMetadataId) -> bool:
        pass

    @abstractmethod
    def Save(self, imageMetadata: ImageMetadata) -> None:
        pass

    @abstractmethod
    def GenerateNewId(self) -> ImageMetadataId:
        pass


class IGenerationMetadataRepository(ABC):
    """Interface for generation metadata repository."""

    @abstractmethod
    def Save(self, generationMetadata) -> None:
        pass

    @abstractmethod
    def GenerationMetadataExists(self, generationMetadataId) -> bool:
        pass

    @abstractmethod
    def FindById(self, generationMetadataId) -> Optional[GenerationMetadata]:
        pass

    @abstractmethod
    def GenerateNewId(self) -> GenerationMetadataId:
        pass


class ILoraMetadataRepository(ABC):
    """Interface for LoRA metadata repository."""

    @abstractmethod
    def FindByHash(self, hash: str) -> Optional[LoraMetadata]:
        pass

    @abstractmethod
    def Save(self, loraMetadata: LoraMetadata) -> None:
        pass

    @abstractmethod
    def GenerateNewId(self) -> LoraMetadataId:
        pass


class IImageContentRepository(ABC):
    """Interface for image content repository."""

    @abstractmethod
    async def GetMetadata(self, imageUri: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def Upload(self, key: str, imageContent: BinaryIO) -> str:
        pass

    @abstractmethod
    async def Delete(self, imageUri: str) -> None:
        pass

    @abstractmethod
    async def GetPresignedGetUrl(self, key: str) -> str:
        pass

    @abstractmethod
    async def GetPresignedPostUrl(self, key: str, ownerId: MemberId) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def Exists(self, imageUri: str) -> bool:
        pass

    @abstractmethod
    async def IsOwnedBy(self, imageUri: str, ownerId: MemberId) -> bool:
        pass


class IThumbnailGenerationService(ABC):
    """Interface for image thumbnail generation."""

    format: MimeType

    @abstractmethod
    async def GenerateThumbnail(self, image: BinaryIO) -> BinaryIO:
        pass
