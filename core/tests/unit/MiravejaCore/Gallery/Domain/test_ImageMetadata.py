import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from unittest.mock import patch

from MiravejaCore.Gallery.Domain.Models import ImageMetadata, Size, GenerationMetadata
from MiravejaCore.Gallery.Domain.Enums import ImageRepositoryType
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId, MemberId, GenerationMetadataId, VectorId


class TestImageMetadata:
    """Test cases for ImageMetadata domain model."""

    def _create_minimal_image_metadata(self, **overrides):
        """Helper method to create ImageMetadata with minimal defaults and optional overrides."""
        defaults = {
            "id": ImageMetadataId(id=1),
            "ownerId": MemberId.Generate(),
            "title": "Test Image",
            "subtitle": "Test Subtitle",
            "description": "Test description",
            "size": Size(width=1920, height=1080),
            "repositoryType": ImageRepositoryType.S3,
            "uri": "https://example.com/image.jpg",
            "isAiGenerated": False,
        }
        defaults.update(overrides)
        return ImageMetadata(**defaults)

    def test_InitializeWithValidMinimalData_ShouldSetCorrectValues(self):
        """Test that ImageMetadata initializes with minimal valid data."""
        image_id = ImageMetadataId(id=1)
        owner_id = MemberId.Generate()
        title = "Test Image"
        subtitle = "Test Subtitle"
        description = "Test description"
        size = Size(width=1920, height=1080)
        repository_type = ImageRepositoryType.S3
        uri = "https://example.com/image.jpg"
        is_ai_generated = False

        image = ImageMetadata(
            id=image_id,
            ownerId=owner_id,
            title=title,
            subtitle=subtitle,
            description=description,
            size=size,
            repositoryType=repository_type,
            uri=uri,
            isAiGenerated=is_ai_generated,
            generationMetadata=None,
            vectorId=None,
        )

        assert image.id == image_id
        assert image.ownerId == owner_id
        assert image.title == title
        assert image.subtitle == subtitle
        assert image.description == description
        assert image.size == size
        assert image.repositoryType == repository_type
        assert image.uri == uri
        assert image.isAiGenerated == is_ai_generated
        assert image.generationMetadata is None
        assert image.vectorId is None
        assert isinstance(image.uploadedAt, datetime)
        assert isinstance(image.updatedAt, datetime)
        assert image.uploadedAt.tzinfo == timezone.utc
        assert image.updatedAt.tzinfo == timezone.utc

    def test_InitializeWithCompleteData_ShouldSetCorrectValues(self):
        """Test that ImageMetadata initializes with complete data."""
        image_id = ImageMetadataId(id=1)
        owner_id = MemberId.Generate()
        title = "AI Generated Image"
        subtitle = "Beautiful Landscape"
        description = "An AI-generated landscape image"
        size = Size(width=512, height=512)
        repository_type = ImageRepositoryType.S3
        uri = "https://example.com/ai-image.jpg"
        is_ai_generated = True
        generation_metadata = GenerationMetadata(
            id=GenerationMetadataId(id=1),
            imageId=image_id,
            prompt="A beautiful landscape",
            negativePrompt=None,
            seed=None,
            model=None,
            sampler=None,
            scheduler=None,
            steps=None,
            cfgScale=None,
            size=None,
            loras=None,
            techniques=None,
        )
        vector_id = VectorId(id=123)
        upload_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        update_time = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

        image = ImageMetadata(
            id=image_id,
            ownerId=owner_id,
            title=title,
            subtitle=subtitle,
            description=description,
            size=size,
            repositoryType=repository_type,
            uri=uri,
            isAiGenerated=is_ai_generated,
            generationMetadata=generation_metadata,
            vectorId=vector_id,
            uploadedAt=upload_time,
            updatedAt=update_time,
        )

        assert image.id == image_id
        assert image.ownerId == owner_id
        assert image.title == title
        assert image.subtitle == subtitle
        assert image.description == description
        assert image.size == size
        assert image.repositoryType == repository_type
        assert image.uri == uri
        assert image.isAiGenerated == is_ai_generated
        assert image.generationMetadata == generation_metadata
        assert image.vectorId == vector_id
        assert image.uploadedAt == upload_time
        assert image.updatedAt == update_time

    def test_InitializeWithEmptyTitle_ShouldRaiseValidationError(self):
        """Test that ImageMetadata raises validation error with empty title."""
        with pytest.raises(ValidationError) as exc_info:
            self._create_minimal_image_metadata(title="")

        assert "at least 1 character" in str(exc_info.value)

    # Note: subtitle now allows empty strings (min_length=0)

    def test_InitializeWithEmptyUri_ShouldRaiseValidationError(self):
        """Test that ImageMetadata raises validation error with empty URI."""
        with pytest.raises(ValidationError) as exc_info:
            self._create_minimal_image_metadata(uri="")

        assert "at least 1 character" in str(exc_info.value)

    def test_ValidateTimestampsWithFutureDate_ShouldRaiseValidationError(self):
        """Test that timestamp validation rejects future dates."""
        future_date = datetime.now(timezone.utc).replace(year=2050)

        with pytest.raises(ValidationError) as exc_info:
            self._create_minimal_image_metadata(uploadedAt=future_date)

        assert "Timestamp cannot be in the future" in str(exc_info.value)

    def test_SerializeModel_ShouldReturnCorrectDict(self):
        """Test that SerializeModel returns correct dictionary structure."""
        image = self._create_minimal_image_metadata()

        result = image.SerializeModel()

        assert result["id"] == int(image.id)
        assert result["ownerId"] == str(image.ownerId)
        assert result["title"] == image.title
        assert result["subtitle"] == image.subtitle
        assert result["description"] == image.description
        assert result["width"] == image.size.width
        assert result["height"] == image.size.height
        assert result["repositoryType"] == image.repositoryType
        assert result["uri"] == image.uri
        assert result["isAiGenerated"] == image.isAiGenerated
        assert result["generationMetadata"] is None
        assert result["vectorId"] is None
        assert result["uploadedAt"] == image.uploadedAt.isoformat()
        assert result["updatedAt"] == image.updatedAt.isoformat()

    def test_SerializeModelWithGenerationMetadata_ShouldIncludeMetadata(self):
        """Test that SerializeModel includes generation metadata when present."""
        generation_metadata = GenerationMetadata(
            id=GenerationMetadataId(id=1),
            imageId=ImageMetadataId(id=1),
            prompt="A beautiful landscape",
            negativePrompt=None,
            seed=None,
            model=None,
            sampler=None,
            scheduler=None,
            steps=None,
            cfgScale=None,
            size=None,
            loras=None,
            techniques=None,
        )
        vector_id = VectorId(id=123)

        image = self._create_minimal_image_metadata(
            isAiGenerated=True, generationMetadata=generation_metadata, vectorId=vector_id
        )

        result = image.SerializeModel()

        assert result["generationMetadata"] is not None
        assert result["vectorId"] == int(vector_id)

    def test_RegisterWithValidData_ShouldCreateCorrectInstance(self):
        """Test that Register factory method creates instance with valid data."""
        image_id = ImageMetadataId(id=1)
        owner_id = MemberId.Generate()
        title = "Test Image"
        subtitle = "Test Subtitle"
        description = "Test description"
        size = Size(width=1920, height=1080)
        repository_type = ImageRepositoryType.S3
        uri = "https://example.com/image.jpg"
        is_ai_generated = False

        image = ImageMetadata.Register(
            id=image_id,
            ownerId=owner_id,
            title=title,
            subtitle=subtitle,
            description=description,
            size=size,
            repositoryType=repository_type,
            uri=uri,
            isAiGenerated=is_ai_generated,
        )

        assert image.id == image_id
        assert image.ownerId == owner_id
        assert image.title == title
        assert image.subtitle == subtitle
        assert image.description == description
        assert image.size == size
        assert image.repositoryType == repository_type
        assert image.uri == uri
        assert image.isAiGenerated == is_ai_generated
        assert image.generationMetadata is None
        assert image.vectorId is None

    def test_IsAiGeneratedWithMetadataWithGenerationData_ShouldReturnTrue(self):
        """Test that IsAiGeneratedWithMetadata returns true when AI-generated with metadata."""
        generation_metadata = GenerationMetadata(
            id=GenerationMetadataId(id=1),
            imageId=ImageMetadataId(id=1),
            prompt="A beautiful landscape",
            negativePrompt=None,
            seed=None,
            model=None,
            sampler=None,
            scheduler=None,
            steps=None,
            cfgScale=None,
            size=None,
            loras=None,
            techniques=None,
        )

        image = self._create_minimal_image_metadata(isAiGenerated=True, generationMetadata=generation_metadata)

        result = image.IsAiGeneratedWithMetadata()

        assert result is True

    def test_IsAiGeneratedWithMetadataWithoutGenerationData_ShouldReturnFalse(self):
        """Test that IsAiGeneratedWithMetadata returns false when AI-generated without metadata."""
        image = self._create_minimal_image_metadata(isAiGenerated=True, generationMetadata=None)

        result = image.IsAiGeneratedWithMetadata()

        assert result is False

    def test_IsAiGeneratedWithMetadataWithNonAiImage_ShouldReturnFalse(self):
        """Test that IsAiGeneratedWithMetadata returns false for non-AI images."""
        image = self._create_minimal_image_metadata(isAiGenerated=False)

        result = image.IsAiGeneratedWithMetadata()

        assert result is False

    def test_HasVectorDataWithVectorId_ShouldReturnTrue(self):
        """Test that HasVectorData returns true when vector ID is present."""
        vector_id = VectorId(id=123)
        image = self._create_minimal_image_metadata(vectorId=vector_id)

        result = image.HasVectorData()

        assert result is True

    def test_HasVectorDataWithoutVectorId_ShouldReturnFalse(self):
        """Test that HasVectorData returns false when vector ID is not present."""
        image = self._create_minimal_image_metadata(vectorId=None)

        result = image.HasVectorData()

        assert result is False

    def test_GetDisplayName_ShouldReturnCombinedTitleAndSubtitle(self):
        """Test that GetDisplayName returns combined title and subtitle."""
        title = "Beautiful Landscape"
        subtitle = "AI Generated"
        image = self._create_minimal_image_metadata(title=title, subtitle=subtitle)

        result = image.GetDisplayName()

        assert result == f"{title} - {subtitle}"

    @patch("MiravejaCore.Gallery.Domain.Models.datetime")
    def test_UpdateTitle_ShouldUpdateTitleAndTimestamp(self, mock_datetime):
        """Test that Update method updates title and updatedAt timestamp."""
        mock_now = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        image = self._create_minimal_image_metadata(title="Old Title")
        new_title = "New Title"

        image.Update(title=new_title, subtitle=image.subtitle, description=image.description)

        assert image.title == new_title
        assert image.updatedAt == mock_now

    @patch("MiravejaCore.Gallery.Domain.Models.datetime")
    def test_UpdateSubtitle_ShouldUpdateSubtitleAndTimestamp(self, mock_datetime):
        """Test that Update method updates subtitle and updatedAt timestamp."""
        mock_now = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        image = self._create_minimal_image_metadata(subtitle="Old Subtitle")
        new_subtitle = "New Subtitle"

        image.Update(title=image.title, subtitle=new_subtitle, description=image.description)

        assert image.subtitle == new_subtitle
        assert image.updatedAt == mock_now

    @patch("MiravejaCore.Gallery.Domain.Models.datetime")
    def test_UpdateDescription_ShouldUpdateDescriptionAndTimestamp(self, mock_datetime):
        """Test that Update method updates description and updatedAt timestamp."""
        mock_now = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        image = self._create_minimal_image_metadata(description="Old description")
        new_description = "New description"

        image.Update(title=image.title, subtitle=image.subtitle, description=new_description)

        assert image.description == new_description
        assert image.updatedAt == mock_now

    @patch("MiravejaCore.Gallery.Domain.Models.datetime")
    def test_AssignVectorId_ShouldSetVectorIdAndTimestamp(self, mock_datetime):
        """Test that AssignVectorId sets vector ID and updates timestamp."""
        mock_now = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        image = self._create_minimal_image_metadata(vectorId=None)
        vector_id = VectorId(id=456)

        image.AssignVectorId(vector_id)

        assert image.vectorId == vector_id
        assert image.updatedAt == mock_now

    @patch("MiravejaCore.Gallery.Domain.Models.datetime")
    def test_UnassignVectorId_ShouldClearVectorIdAndTimestamp(self, mock_datetime):
        """Test that UnassignVectorId clears vector ID and updates timestamp."""
        mock_now = datetime(2023, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        vector_id = VectorId(id=456)
        image = self._create_minimal_image_metadata(vectorId=vector_id)

        image.UnassignVectorId()

        assert image.vectorId is None
        assert image.updatedAt == mock_now
