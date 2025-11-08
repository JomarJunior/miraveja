import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from typing import Iterator

from MiravejaCore.Gallery.Infrastructure.Sql.Repository import (
    SqlImageMetadataRepository,
    SqlGenerationMetadataRepository,
    SqlLoraMetadataRepository,
)
from MiravejaCore.Gallery.Infrastructure.Sql.Entities import (
    ImageMetadataEntity,
    GenerationMetadataEntity,
    LoraMetadataEntity,
)
from MiravejaCore.Gallery.Domain.Models import ImageMetadata, GenerationMetadata, LoraMetadata, Size
from MiravejaCore.Gallery.Domain.Enums import ImageRepositoryType, SamplerType, SchedulerType
from MiravejaCore.Shared.Identifiers.Models import (
    ImageMetadataId,
    GenerationMetadataId,
    LoraMetadataId,
    MemberId,
)
from MiravejaCore.Shared.Utils.Repository.Queries import ListAllQuery
from MiravejaCore.Shared.Utils.Repository.Enums import SortOrder


class TestSqlImageMetadataRepository:
    """Test cases for SqlImageMetadataRepository."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_db_session):
        """Create a SqlImageMetadataRepository instance with mocked session."""
        return SqlImageMetadataRepository(dbSession=mock_db_session)

    def test_InitializeWithValidSession_ShouldSetCorrectValues(self, mock_db_session):
        """Test that SqlImageMetadataRepository initializes with valid session."""
        # Arrange & Act
        repository = SqlImageMetadataRepository(dbSession=mock_db_session)

        # Assert
        assert repository._dbSession == mock_db_session

    def test_ListAllWithDefaultQuery_ShouldReturnIteratorOfImageMetadata(self, repository, mock_db_session):
        """Test that ListAll returns iterator with default query parameters."""
        # Arrange
        mockEntity = MagicMock(spec=ImageMetadataEntity)
        mockEntity.ToDict.return_value = {
            "id": 1,
            "ownerId": "550e8400-e29b-41d4-a716-446655440001",
            "title": "Test Image",
            "subtitle": "Subtitle",
            "description": None,
            "size": {"width": 512, "height": 512},
            "repositoryType": ImageRepositoryType.S3.value,
            "uri": "s3://bucket/image.jpg",
            "isAiGenerated": False,
            "generationMetadata": None,
            "vectorId": None,
            "uploadedAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        mockQuery = MagicMock()
        mockQuery.order_by.return_value = mockQuery
        mockQuery.offset.return_value = mockQuery
        mockQuery.limit.return_value = mockQuery
        mockQuery.yield_per.return_value = [mockEntity]

        mock_db_session.query.return_value = mockQuery

        # Act
        result = repository.ListAll()

        # Assert
        assert isinstance(result, Iterator)
        imageMetadataList = list(result)
        assert len(imageMetadataList) == 1
        assert isinstance(imageMetadataList[0], ImageMetadata)
        assert imageMetadataList[0].id.id == 1
        mock_db_session.query.assert_called_once_with(ImageMetadataEntity)

    def test_ListAllWithCustomQuery_ShouldApplySortingAndPagination(self, repository, mock_db_session):
        """Test that ListAll applies custom sorting and pagination."""
        # Arrange
        query = ListAllQuery(sortBy="uploadedAt", sortOrder=SortOrder.DESC, limit=50, offset=10)

        mockQuery = MagicMock()
        mockQuery.order_by.return_value = mockQuery
        mockQuery.offset.return_value = mockQuery
        mockQuery.limit.return_value = mockQuery
        mockQuery.yield_per.return_value = []

        mock_db_session.query.return_value = mockQuery

        # Act
        result = list(repository.ListAll(query=query))

        # Assert
        mockQuery.order_by.assert_called_once()
        mockQuery.offset.assert_called_once_with(10)
        mockQuery.limit.assert_called_once_with(50)

    def test_ListAllWithFilterFunction_ShouldApplyInMemoryFiltering(self, repository, mock_db_session):
        """Test that ListAll applies filter function to results."""
        # Arrange
        mockEntity1 = MagicMock(spec=ImageMetadataEntity)
        mockEntity1.ToDict.return_value = {
            "id": 1,
            "ownerId": "550e8400-e29b-41d4-a716-446655440002",
            "title": "Keep This",
            "subtitle": "Subtitle",
            "description": None,
            "size": {"width": 512, "height": 512},
            "repositoryType": ImageRepositoryType.S3.value,
            "uri": "s3://bucket/image1.jpg",
            "isAiGenerated": True,
            "generationMetadata": None,
            "vectorId": None,
            "uploadedAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        mockEntity2 = MagicMock(spec=ImageMetadataEntity)
        mockEntity2.ToDict.return_value = {
            "id": 2,
            "ownerId": "550e8400-e29b-41d4-a716-446655440003",
            "title": "Filter This",
            "subtitle": "Subtitle",
            "description": None,
            "size": {"width": 512, "height": 512},
            "repositoryType": ImageRepositoryType.S3.value,
            "uri": "s3://bucket/image2.jpg",
            "isAiGenerated": False,
            "generationMetadata": None,
            "vectorId": None,
            "uploadedAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        mockQuery = MagicMock()
        mockQuery.order_by.return_value = mockQuery
        mockQuery.offset.return_value = mockQuery
        mockQuery.limit.return_value = mockQuery
        mockQuery.yield_per.return_value = [mockEntity1, mockEntity2]

        mock_db_session.query.return_value = mockQuery

        # Filter function: only keep AI-generated images
        filterFunction = lambda img: img.isAiGenerated

        # Act
        result = list(repository.ListAll(filterFunction=filterFunction))

        # Assert
        assert len(result) == 1
        assert result[0].isAiGenerated is True

    def test_CountWithNoRecords_ShouldReturnZero(self, repository, mock_db_session):
        """Test that Count returns zero when no records exist."""
        # Arrange
        mockQuery = MagicMock()
        mockQuery.count.return_value = 0
        mock_db_session.query.return_value = mockQuery

        # Act
        result = repository.Count()

        # Assert
        assert result == 0
        mock_db_session.query.assert_called_once_with(ImageMetadataEntity)

    def test_CountWithRecords_ShouldReturnCorrectCount(self, repository, mock_db_session):
        """Test that Count returns correct number of records."""
        # Arrange
        mockQuery = MagicMock()
        mockQuery.count.return_value = 42
        mock_db_session.query.return_value = mockQuery

        # Act
        result = repository.Count()

        # Assert
        assert result == 42

    def test_FindByIdWithExistingImage_ShouldReturnImageMetadata(self, repository, mock_db_session):
        """Test that FindById returns ImageMetadata when image exists."""
        # Arrange
        imageId = ImageMetadataId(id=10)
        mockEntity = MagicMock(spec=ImageMetadataEntity)
        mockEntity.ToDict.return_value = {
            "id": 10,
            "ownerId": "550e8400-e29b-41d4-a716-446655440004",
            "title": "Found Image",
            "subtitle": "Found Subtitle",
            "description": "Description",
            "size": {"width": 1024, "height": 768},
            "repositoryType": ImageRepositoryType.DISK.value,
            "uri": "disk://images/found.jpg",
            "isAiGenerated": True,
            "generationMetadata": None,
            "vectorId": 123,
            "uploadedAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        mock_db_session.get.return_value = mockEntity

        # Act
        result = repository.FindById(imageId)

        # Assert
        assert result is not None
        assert isinstance(result, ImageMetadata)
        assert result.id.id == 10
        assert result.title == "Found Image"
        mock_db_session.get.assert_called_once_with(ImageMetadataEntity, 10)

    def test_FindByIdWithNonExistingImage_ShouldReturnNone(self, repository, mock_db_session):
        """Test that FindById returns None when image doesn't exist."""
        # Arrange
        imageId = ImageMetadataId(id=999)
        mock_db_session.get.return_value = None

        # Act
        result = repository.FindById(imageId)

        # Assert
        assert result is None
        mock_db_session.get.assert_called_once_with(ImageMetadataEntity, 999)

    def test_FindByUriWithExistingImage_ShouldReturnImageMetadata(self, repository, mock_db_session):
        """Test that FindByUri returns ImageMetadata when URI exists."""
        # Arrange
        uri = "s3://bucket/unique.jpg"
        mockEntity = MagicMock(spec=ImageMetadataEntity)
        mockEntity.ToDict.return_value = {
            "id": 20,
            "ownerId": "550e8400-e29b-41d4-a716-446655440005",
            "title": "URI Found Image",
            "subtitle": "URI Subtitle",
            "description": None,
            "size": {"width": 512, "height": 512},
            "repositoryType": ImageRepositoryType.S3.value,
            "uri": uri,
            "isAiGenerated": False,
            "generationMetadata": None,
            "vectorId": None,
            "uploadedAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        mockQuery = MagicMock()
        mockQuery.filter.return_value = mockQuery
        mockQuery.first.return_value = mockEntity

        mock_db_session.query.return_value = mockQuery

        # Act
        result = repository.FindByUri(uri)

        # Assert
        assert result is not None
        assert isinstance(result, ImageMetadata)
        assert result.uri == uri
        mock_db_session.query.assert_called_once_with(ImageMetadataEntity)

    def test_FindByUriWithNonExistingUri_ShouldReturnNone(self, repository, mock_db_session):
        """Test that FindByUri returns None when URI doesn't exist."""
        # Arrange
        uri = "s3://bucket/nonexistent.jpg"
        mockQuery = MagicMock()
        mockQuery.filter.return_value = mockQuery
        mockQuery.first.return_value = None

        mock_db_session.query.return_value = mockQuery

        # Act
        result = repository.FindByUri(uri)

        # Assert
        assert result is None

    def test_ImageMetadataExistsWithExistingImage_ShouldReturnTrue(self, repository, mock_db_session):
        """Test that ImageMetadataExists returns True when image exists."""
        # Arrange
        imageId = ImageMetadataId(id=30)
        mockEntity = MagicMock(spec=ImageMetadataEntity)
        mock_db_session.get.return_value = mockEntity

        # Act
        result = repository.ImageMetadataExists(imageId)

        # Assert
        assert result is True
        mock_db_session.get.assert_called_once_with(ImageMetadataEntity, 30)

    def test_ImageMetadataExistsWithNonExistingImage_ShouldReturnFalse(self, repository, mock_db_session):
        """Test that ImageMetadataExists returns False when image doesn't exist."""
        # Arrange
        imageId = ImageMetadataId(id=999)
        mock_db_session.get.return_value = None

        # Act
        result = repository.ImageMetadataExists(imageId)

        # Assert
        assert result is False

    def test_SaveWithValidImageMetadata_ShouldMergeEntity(self, repository, mock_db_session):
        """Test that Save merges ImageMetadata entity."""
        # Arrange
        imageMetadata = ImageMetadata(
            id=ImageMetadataId(id=40),
            ownerId=MemberId(id="550e8400-e29b-41d4-a716-446655440006"),
            title="Save Test",
            subtitle="Save Subtitle",
            description="Description",
            size=Size(width=800, height=600),
            repositoryType=ImageRepositoryType.DEVIANTART,
            uri="deviantart://images/save.jpg",
            isAiGenerated=False,
            generationMetadata=None,
            vectorId=None,
        )

        # Act
        repository.Save(imageMetadata)

        # Assert
        mock_db_session.merge.assert_called_once()
        mergedEntity = mock_db_session.merge.call_args[0][0]
        assert isinstance(mergedEntity, ImageMetadataEntity)

    def test_GenerateNewIdWithValidSequence_ShouldReturnNewImageMetadataId(self, repository, mock_db_session):
        """Test that GenerateNewId returns new ImageMetadataId from sequence."""
        # Arrange
        mockResult = MagicMock()
        mockResult.scalar_one.return_value = 100
        mock_db_session.execute.return_value = mockResult

        # Act
        result = repository.GenerateNewId()

        # Assert
        assert isinstance(result, ImageMetadataId)
        assert result.id == 100
        mock_db_session.execute.assert_called_once()


class TestSqlGenerationMetadataRepository:
    """Test cases for SqlGenerationMetadataRepository."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_db_session):
        """Create a SqlGenerationMetadataRepository instance with mocked session."""
        return SqlGenerationMetadataRepository(dbSession=mock_db_session)

    def test_InitializeWithValidSession_ShouldSetCorrectValues(self, mock_db_session):
        """Test that SqlGenerationMetadataRepository initializes with valid session."""
        # Arrange & Act
        repository = SqlGenerationMetadataRepository(dbSession=mock_db_session)

        # Assert
        assert repository._dbSession == mock_db_session

    def test_SaveWithGenerationMetadataNoLoras_ShouldMergeEntity(self, repository, mock_db_session):
        """Test that Save merges GenerationMetadata without LoRAs."""
        # Arrange
        generationMetadata = GenerationMetadata(
            id=GenerationMetadataId(id=50),
            imageId=ImageMetadataId(id=100),
            prompt="Test prompt",
            negativePrompt="Test negative",
            seed="12345",
            model="test_model",
            sampler=SamplerType.EULER_A,
            scheduler=SchedulerType.KARRAS,
            steps=20,
            cfgScale=7.5,
            size=Size(width=512, height=768),
            loras=None,
            techniques=None,
        )

        # Act
        repository.Save(generationMetadata)

        # Assert
        mock_db_session.merge.assert_called_once()
        mergedEntity = mock_db_session.merge.call_args[0][0]
        assert isinstance(mergedEntity, GenerationMetadataEntity)
        assert mergedEntity.loras == []

    def test_SaveWithGenerationMetadataWithLoras_ShouldMergeEntityWithLoras(self, repository, mock_db_session):
        """Test that Save merges GenerationMetadata with LoRAs."""
        # Arrange
        lora1 = LoraMetadata(id=LoraMetadataId(id=1), hash="lora_hash_1", name="LoRA 1", generationMetadatas=[])
        lora2 = LoraMetadata(id=LoraMetadataId(id=2), hash="lora_hash_2", name="LoRA 2", generationMetadatas=[])

        generationMetadata = GenerationMetadata(
            id=GenerationMetadataId(id=60),
            imageId=ImageMetadataId(id=200),
            prompt="Prompt with LoRAs",
            loras=[lora1, lora2],
        )

        # Act
        repository.Save(generationMetadata)

        # Assert
        mock_db_session.merge.assert_called_once()
        mergedEntity = mock_db_session.merge.call_args[0][0]
        assert isinstance(mergedEntity, GenerationMetadataEntity)
        assert len(mergedEntity.loras) == 2
        assert all(isinstance(lora, LoraMetadataEntity) for lora in mergedEntity.loras)

    def test_GenerationMetadataExistsWithExistingMetadata_ShouldReturnTrue(self, repository, mock_db_session):
        """Test that GenerationMetadataExists returns True when metadata exists."""
        # Arrange
        generationMetadataId = GenerationMetadataId(id=70)
        mockEntity = MagicMock(spec=GenerationMetadataEntity)
        mock_db_session.get.return_value = mockEntity

        # Act
        result = repository.GenerationMetadataExists(generationMetadataId)

        # Assert
        assert result is True
        mock_db_session.get.assert_called_once_with(GenerationMetadataEntity, 70)

    def test_GenerationMetadataExistsWithNonExistingMetadata_ShouldReturnFalse(self, repository, mock_db_session):
        """Test that GenerationMetadataExists returns False when metadata doesn't exist."""
        # Arrange
        generationMetadataId = GenerationMetadataId(id=999)
        mock_db_session.get.return_value = None

        # Act
        result = repository.GenerationMetadataExists(generationMetadataId)

        # Assert
        assert result is False

    def test_FindByIdWithExistingMetadata_ShouldReturnGenerationMetadata(self, repository, mock_db_session):
        """Test that FindById returns GenerationMetadata when metadata exists."""
        # Arrange
        generationMetadataId = GenerationMetadataId(id=80)
        mockEntity = MagicMock(spec=GenerationMetadataEntity)
        mockEntity.ToDict.return_value = {
            "id": 80,
            "imageId": 300,
            "prompt": "Found prompt",
            "negativePrompt": None,
            "seed": None,
            "model": None,
            "sampler": None,
            "scheduler": None,
            "steps": None,
            "cfgScale": None,
            "size": None,
            "loras": [],
            "techniques": None,
        }

        mock_db_session.get.return_value = mockEntity

        # Act
        result = repository.FindById(generationMetadataId)

        # Assert
        assert result is not None
        assert isinstance(result, GenerationMetadata)
        assert result.id.id == 80
        assert result.prompt == "Found prompt"
        mock_db_session.get.assert_called_once_with(GenerationMetadataEntity, 80)

    def test_FindByIdWithNonExistingMetadata_ShouldReturnNone(self, repository, mock_db_session):
        """Test that FindById returns None when metadata doesn't exist."""
        # Arrange
        generationMetadataId = GenerationMetadataId(id=999)
        mock_db_session.get.return_value = None

        # Act
        result = repository.FindById(generationMetadataId)

        # Assert
        assert result is None

    def test_GenerateNewIdWithValidSequence_ShouldReturnNewGenerationMetadataId(self, repository, mock_db_session):
        """Test that GenerateNewId returns new GenerationMetadataId from sequence."""
        # Arrange
        mockResult = MagicMock()
        mockResult.scalar_one.return_value = 200
        mock_db_session.execute.return_value = mockResult

        # Act
        result = repository.GenerateNewId()

        # Assert
        assert isinstance(result, GenerationMetadataId)
        assert result.id == 200
        mock_db_session.execute.assert_called_once()


class TestSqlLoraMetadataRepository:
    """Test cases for SqlLoraMetadataRepository."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return MagicMock()

    @pytest.fixture
    def repository(self, mock_db_session):
        """Create a SqlLoraMetadataRepository instance with mocked session."""
        return SqlLoraMetadataRepository(dbSession=mock_db_session)

    def test_InitializeWithValidSession_ShouldSetCorrectValues(self, mock_db_session):
        """Test that SqlLoraMetadataRepository initializes with valid session."""
        # Arrange & Act
        repository = SqlLoraMetadataRepository(dbSession=mock_db_session)

        # Assert
        assert repository._dbSession == mock_db_session

    def test_SaveWithValidLoraMetadata_ShouldMergeEntity(self, repository, mock_db_session):
        """Test that Save merges LoraMetadata entity."""
        # Arrange
        loraMetadata = LoraMetadata(
            id=LoraMetadataId(id=90),
            hash="save_lora_hash",
            name="Save LoRA",
            generationMetadatas=[],
        )

        # Act
        repository.Save(loraMetadata)

        # Assert
        mock_db_session.merge.assert_called_once()
        mergedEntity = mock_db_session.merge.call_args[0][0]
        assert isinstance(mergedEntity, LoraMetadataEntity)

    def test_FindByHashWithExistingLora_ShouldReturnLoraMetadata(self, repository, mock_db_session):
        """Test that FindByHash returns LoraMetadata when hash exists."""
        # Arrange
        hash_value = "existing_hash_123"
        mockEntity = MagicMock(spec=LoraMetadataEntity)
        mockEntity.ToDict.return_value = {
            "id": 100,
            "hash": hash_value,
            "name": "Found LoRA",
            "generationMetadatas": [],
        }

        mockQuery = MagicMock()
        mockQuery.filter.return_value = mockQuery
        mockQuery.first.return_value = mockEntity

        mock_db_session.query.return_value = mockQuery

        # Act
        result = repository.FindByHash(hash_value)

        # Assert
        assert result is not None
        assert isinstance(result, LoraMetadata)
        assert result.hash == hash_value
        assert result.name == "Found LoRA"
        mock_db_session.query.assert_called_once_with(LoraMetadataEntity)

    def test_FindByHashWithNonExistingHash_ShouldReturnNone(self, repository, mock_db_session):
        """Test that FindByHash returns None when hash doesn't exist."""
        # Arrange
        hash_value = "nonexistent_hash"
        mockQuery = MagicMock()
        mockQuery.filter.return_value = mockQuery
        mockQuery.first.return_value = None

        mock_db_session.query.return_value = mockQuery

        # Act
        result = repository.FindByHash(hash_value)

        # Assert
        assert result is None

    def test_GenerateNewIdWithValidSequence_ShouldReturnNewLoraMetadataId(self, repository, mock_db_session):
        """Test that GenerateNewId returns new LoraMetadataId from sequence."""
        # Arrange
        mockResult = MagicMock()
        mockResult.scalar_one.return_value = 300
        mock_db_session.execute.return_value = mockResult

        # Act
        result = repository.GenerateNewId()

        # Assert
        assert isinstance(result, LoraMetadataId)
        assert result.id == 300
        mock_db_session.execute.assert_called_once()
