from abc import ABC, abstractmethod
from typing import Iterator, Optional

from Miraveja.Gallery.Domain.Models import GenerationMetadata, ImageMetadata, LoraMetadata
from Miraveja.Shared.Identifiers.Models import GenerationMetadataId, ImageMetadataId, LoraMetadataId
from Miraveja.Shared.Utils.Repository.Queries import ListAllQuery
from Miraveja.Shared.Utils.Repository.Types import FilterFunction


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
