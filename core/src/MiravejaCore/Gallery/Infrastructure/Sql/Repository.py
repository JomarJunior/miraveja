from typing import Iterator, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session as DatabaseSession

from MiravejaCore.Gallery.Domain.Interfaces import (
    IGenerationMetadataRepository,
    IImageMetadataRepository,
    ILoraMetadataRepository,
)
from MiravejaCore.Gallery.Domain.Models import GenerationMetadata, ImageMetadata, LoraMetadata
from MiravejaCore.Gallery.Infrastructure.Sql.Entities import (
    GenerationMetadataEntity,
    ImageMetadataEntity,
    LoraMetadataEntity,
)
from MiravejaCore.Shared.Identifiers.Models import GenerationMetadataId, ImageMetadataId, LoraMetadataId
from MiravejaCore.Shared.Utils.Repository.Queries import ListAllQuery
from MiravejaCore.Shared.Utils.Repository.Types import FilterFunction


class SqlImageMetadataRepository(IImageMetadataRepository):
    def __init__(self, dbSession: DatabaseSession):
        self._dbSession = dbSession

    def ListAll(
        self, query: ListAllQuery = ListAllQuery(), filterFunction: Optional[FilterFunction] = None
    ) -> Iterator[ImageMetadata]:
        dbQuery = self._dbSession.query(ImageMetadataEntity)

        # Apply sorting
        sortColumn = getattr(ImageMetadataEntity, query.sortBy, None)
        if sortColumn is not None:
            if query.sortOrder == query.sortOrder.ASC:
                dbQuery = dbQuery.order_by(sortColumn.asc())
            else:
                dbQuery = dbQuery.order_by(sortColumn.desc())

        # Apply pagination
        dbQuery = dbQuery.offset(query.offset).limit(query.limit)

        # Yield results as an iterator
        for entity in dbQuery.yield_per(100):  # SQLAlchemy will load 100 rows at a time
            imageMetadata: ImageMetadata = ImageMetadata.model_validate(entity.ToDict())
            # Apply in-memory filtering if a filter function is provided
            if filterFunction is not None and callable(filterFunction) and not filterFunction(imageMetadata):
                continue
            yield imageMetadata

    def Count(self) -> int:
        dbQuery = self._dbSession.query(ImageMetadataEntity)
        return dbQuery.count()

    def FindById(self, imageId: ImageMetadataId) -> Optional[ImageMetadata]:
        entity = self._dbSession.get(ImageMetadataEntity, int(imageId))
        if entity is None:
            return None
        return ImageMetadata.model_validate(entity.ToDict())

    def FindByUri(self, uri: str) -> Optional[ImageMetadata]:
        entity = self._dbSession.query(ImageMetadataEntity).filter(ImageMetadataEntity.uri == uri).first()
        if entity is None:
            return None
        return ImageMetadata.model_validate(entity.ToDict())

    def ImageMetadataExists(self, imageId: ImageMetadataId) -> bool:
        entity = self._dbSession.get(ImageMetadataEntity, int(imageId))
        return entity is not None

    def Save(self, imageMetadata: ImageMetadata) -> None:
        entity = ImageMetadataEntity.FromDomain(imageMetadata)
        self._dbSession.merge(entity)

    def GenerateNewId(self) -> ImageMetadataId:
        result = self._dbSession.execute(text("SELECT nextval('seq_image_metadata_id')"))
        newId = result.scalar_one()
        return ImageMetadataId(id=newId)


class SqlGenerationMetadataRepository(IGenerationMetadataRepository):
    def __init__(self, dbSession: DatabaseSession):
        self._dbSession = dbSession

    def Save(self, generationMetadata: GenerationMetadata) -> None:
        entity = GenerationMetadataEntity.FromDomain(generationMetadata)
        self._dbSession.merge(entity)

    def GenerationMetadataExists(self, generationMetadataId) -> bool:
        entity = self._dbSession.get(GenerationMetadataEntity, int(generationMetadataId))
        return entity is not None

    def FindById(self, generationMetadataId) -> Optional[GenerationMetadata]:
        entity = self._dbSession.get(GenerationMetadataEntity, int(generationMetadataId))
        if entity is None:
            return None

        return GenerationMetadata.model_validate(entity.ToDict())

    def GenerateNewId(self) -> GenerationMetadataId:
        result = self._dbSession.execute(text("SELECT nextval('seq_generation_metadata_id')"))
        newId = result.scalar_one()

        return GenerationMetadataId(id=newId)


class SqlLoraMetadataRepository(ILoraMetadataRepository):
    def __init__(self, dbSession: DatabaseSession):
        self._dbSession = dbSession

    def Save(self, loraMetadata) -> None:
        entity = LoraMetadataEntity.FromDomain(loraMetadata)
        self._dbSession.merge(entity)

    def FindByHash(self, hash: str) -> Optional[LoraMetadata]:
        entity = self._dbSession.query(LoraMetadataEntity).filter(LoraMetadataEntity.hash == hash).first()
        if entity is None:
            return None

        return LoraMetadata.model_validate(entity.ToDict())

    def GenerateNewId(self) -> LoraMetadataId:
        result = self._dbSession.execute(text("SELECT nextval('seq_lora_metadata_id')"))
        newId = result.scalar_one()
        return LoraMetadataId(id=newId)
