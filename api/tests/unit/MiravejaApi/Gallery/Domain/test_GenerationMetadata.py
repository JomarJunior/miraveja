import pytest
from pydantic import ValidationError

from MiravejaApi.Gallery.Domain.Models import GenerationMetadata, Size, LoraMetadata
from MiravejaApi.Gallery.Domain.Enums import SamplerType, SchedulerType, TechniqueType
from MiravejaApi.Shared.Identifiers.Models import GenerationMetadataId, ImageMetadataId, LoraMetadataId


class TestGenerationMetadata:
    """Test cases for GenerationMetadata domain model."""

    def _create_minimal_generation_metadata(self, **overrides):
        """Helper method to create GenerationMetadata with minimal defaults and optional overrides."""
        defaults = {
            "id": GenerationMetadataId(id=1),
            "imageId": ImageMetadataId(id=1),
            "prompt": "A beautiful landscape",
            "negativePrompt": None,
            "seed": None,
            "model": None,
            "sampler": None,
            "scheduler": None,
            "steps": None,
            "cfgScale": None,
            "size": None,
            "loras": None,
            "techniques": None,
        }
        defaults.update(overrides)
        return GenerationMetadata(**defaults)

    def test_InitializeWithValidMinimalData_ShouldSetCorrectValues(self):
        """Test that GenerationMetadata initializes with minimal valid data."""
        generation_id = GenerationMetadataId(id=1)
        image_id = ImageMetadataId(id=1)
        prompt = "A beautiful landscape"

        generation = GenerationMetadata(
            id=generation_id,
            imageId=image_id,
            prompt=prompt,
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

        assert generation.id == generation_id
        assert generation.imageId == image_id
        assert generation.prompt == prompt
        assert generation.negativePrompt is None
        assert generation.seed is None
        assert generation.model is None
        assert generation.sampler is None
        assert generation.scheduler is None
        assert generation.steps is None
        assert generation.cfgScale is None
        assert generation.size is None
        assert generation.loras is None
        assert generation.techniques is None

    def test_InitializeWithCompleteData_ShouldSetCorrectValues(self):
        """Test that GenerationMetadata initializes with complete data."""
        generation_id = GenerationMetadataId(id=1)
        image_id = ImageMetadataId(id=1)
        prompt = "A beautiful landscape"
        negative_prompt = "ugly, blurry"
        seed = 123456
        model = "model_hash_123"
        sampler = SamplerType.EULER_A
        scheduler = SchedulerType.KARRAS
        steps = 20
        cfg_scale = 7.5
        size = Size(width=512, height=512)
        lora = LoraMetadata(id=LoraMetadataId(id=1), hash="lora_hash", name="TestLoRA", generationMetadatas=None)
        loras = [lora]
        techniques = [TechniqueType.TEXT_TO_IMAGE, TechniqueType.HIRES_FIX]

        generation = GenerationMetadata(
            id=generation_id,
            imageId=image_id,
            prompt=prompt,
            negativePrompt=negative_prompt,
            seed=seed,
            model=model,
            sampler=sampler,
            scheduler=scheduler,
            steps=steps,
            cfgScale=cfg_scale,
            size=size,
            loras=loras,
            techniques=techniques,
        )

        assert generation.id == generation_id
        assert generation.imageId == image_id
        assert generation.prompt == prompt
        assert generation.negativePrompt == negative_prompt
        assert generation.seed == seed
        assert generation.model == model
        assert generation.sampler == sampler
        assert generation.scheduler == scheduler
        assert generation.steps == steps
        assert generation.cfgScale == cfg_scale
        assert generation.size == size
        assert generation.loras == loras
        assert generation.techniques == techniques

    def test_InitializeWithEmptyPrompt_ShouldRaiseValidationError(self):
        """Test that GenerationMetadata raises validation error with empty prompt."""
        with pytest.raises(ValidationError) as exc_info:
            self._create_minimal_generation_metadata(prompt="")

        assert "at least 1 character" in str(exc_info.value)

    def test_InitializeWithTooLongPrompt_ShouldRaiseValidationError(self):
        """Test that GenerationMetadata raises validation error with prompt too long."""
        long_prompt = "A" * 2001  # Exceeds max_length of 2000

        with pytest.raises(ValidationError) as exc_info:
            self._create_minimal_generation_metadata(prompt=long_prompt)

        assert "at most 2000 characters" in str(exc_info.value)

    def test_InitializeWithTooLongNegativePrompt_ShouldRaiseValidationError(self):
        """Test that GenerationMetadata raises validation error with negative prompt too long."""
        long_negative_prompt = "A" * 2001  # Exceeds max_length of 2000

        with pytest.raises(ValidationError) as exc_info:
            self._create_minimal_generation_metadata(negativePrompt=long_negative_prompt)

        assert "at most 2000 characters" in str(exc_info.value)

    def test_ValidateCfgScaleWithValidValue_ShouldAcceptValue(self):
        """Test that cfgScale validation accepts valid values."""
        generation = self._create_minimal_generation_metadata(cfgScale=7.5)

        assert generation.cfgScale == 7.5

    def test_ValidateCfgScaleWithBoundaryValues_ShouldAcceptValues(self):
        """Test that cfgScale validation accepts boundary values."""
        # Test minimum value
        generation_min = self._create_minimal_generation_metadata(cfgScale=1.0)
        assert generation_min.cfgScale == 1.0

        # Test maximum value
        generation_max = self._create_minimal_generation_metadata(cfgScale=30.0)
        assert generation_max.cfgScale == 30.0

    def test_ValidateCfgScaleWithTooLowValue_ShouldRaiseValidationError(self):
        """Test that cfgScale validation rejects values below 1.0."""
        with pytest.raises(ValidationError) as exc_info:
            self._create_minimal_generation_metadata(cfgScale=0.5)

        assert "cfgScale must be between 1.0 and 30.0" in str(exc_info.value)

    def test_ValidateCfgScaleWithTooHighValue_ShouldRaiseValidationError(self):
        """Test that cfgScale validation rejects values above 30.0."""
        with pytest.raises(ValidationError) as exc_info:
            self._create_minimal_generation_metadata(cfgScale=31.0)

        assert "cfgScale must be between 1.0 and 30.0" in str(exc_info.value)

    def test_ValidateStepsWithValidValue_ShouldAcceptValue(self):
        """Test that steps validation accepts valid positive values."""
        generation = self._create_minimal_generation_metadata(steps=20)

        assert generation.steps == 20

    def test_ValidateStepsWithZeroValue_ShouldRaiseValidationError(self):
        """Test that steps validation rejects zero value."""
        with pytest.raises(ValidationError) as exc_info:
            self._create_minimal_generation_metadata(steps=0)

        assert "steps must be a positive integer" in str(exc_info.value)

    def test_ValidateStepsWithNegativeValue_ShouldRaiseValidationError(self):
        """Test that steps validation rejects negative values."""
        with pytest.raises(ValidationError) as exc_info:
            self._create_minimal_generation_metadata(steps=-5)

        assert "steps must be a positive integer" in str(exc_info.value)

    def test_RegisterWithValidData_ShouldCreateCorrectInstance(self):
        """Test that Register factory method creates instance with valid data."""
        generation_id = GenerationMetadataId(id=1)
        image_id = ImageMetadataId(id=1)
        prompt = "A beautiful landscape"
        negative_prompt = "ugly, blurry"
        seed = 123456

        generation = GenerationMetadata.Register(
            id=generation_id, imageId=image_id, prompt=prompt, negativePrompt=negative_prompt, seed=seed
        )

        assert generation.id == generation_id
        assert generation.imageId == image_id
        assert generation.prompt == prompt
        assert generation.negativePrompt == negative_prompt
        assert generation.seed == seed
        assert generation.model is None
        assert generation.sampler is None
        assert generation.scheduler is None
        assert generation.steps is None
        assert generation.cfgScale is None
        assert generation.size is None
        assert generation.loras is None
        assert generation.techniques is None

    def test_RegisterWithMinimalData_ShouldCreateCorrectInstance(self):
        """Test that Register factory method creates instance with minimal data."""
        generation_id = GenerationMetadataId(id=1)
        image_id = ImageMetadataId(id=1)
        prompt = "A beautiful landscape"

        generation = GenerationMetadata.Register(id=generation_id, imageId=image_id, prompt=prompt)

        assert generation.id == generation_id
        assert generation.imageId == image_id
        assert generation.prompt == prompt
        assert generation.negativePrompt is None
