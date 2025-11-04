import pytest

from MiravejaCore.Gallery.Domain.Enums import SamplerType, SchedulerType, TechniqueType, ImageRepositoryType


class TestSamplerType:
    """Test cases for SamplerType enum."""

    def test_EnumValues_ShouldHaveCorrectStringValues(self):
        """Test that SamplerType enum values have correct string representations."""
        assert SamplerType.DPMPP_2M.value == "DPM++ 2M"
        assert SamplerType.EULER_A.value == "Euler a"
        assert SamplerType.DDIM.value == "DDIM"
        assert SamplerType.OTHER.value == "Other"

    def test_StrMethod_ShouldReturnValue(self):
        """Test that __str__ method returns enum value."""
        assert str(SamplerType.DPMPP_2M) == "DPM++ 2M"
        assert str(SamplerType.EULER_A) == "Euler a"

    def test_AllEnumValues_ShouldBeAccessible(self):
        """Test that all enum values are accessible."""
        expected_values = [
            "DPM++ 2M",
            "DPM++ SDE",
            "DPM++ 2M SDE",
            "DPM++ 2M SDE Heun",
            "DPM++ 2S a",
            "DPM++ 3M SDE",
            "Euler a",
            "Euler",
            "LMS",
            "Heun",
            "DPM2",
            "DPM2 a",
            "DPM fast",
            "DPM adaptive",
            "Restart",
            "HeunPP2",
            "IPNDM",
            "IPNDM V",
            "DEIS",
            "DDIM",
            "DDIM CFG++",
            "PLMS",
            "UniPC",
            "LCM",
            "DDPM",
            "Other",
        ]

        enum_values = [sampler.value for sampler in SamplerType]

        assert len(enum_values) == len(expected_values)
        for expected_value in expected_values:
            assert expected_value in enum_values


class TestSchedulerType:
    """Test cases for SchedulerType enum."""

    def test_EnumValues_ShouldHaveCorrectStringValues(self):
        """Test that SchedulerType enum values have correct string representations."""
        assert SchedulerType.AUTOMATIC.value == "Automatic"
        assert SchedulerType.KARRAS.value == "Karras"
        assert SchedulerType.NORMAL.value == "Normal"
        assert SchedulerType.OTHER.value == "Other"

    def test_StrMethod_ShouldReturnValue(self):
        """Test that __str__ method returns enum value."""
        assert str(SchedulerType.AUTOMATIC) == "Automatic"
        assert str(SchedulerType.KARRAS) == "Karras"

    def test_AllEnumValues_ShouldBeAccessible(self):
        """Test that all enum values are accessible."""
        expected_values = [
            "Automatic",
            "Uniform",
            "Karras",
            "Exponential",
            "Polyexponential",
            "SGM Uniform",
            "KL Optimal",
            "Align Your Steps",
            "Simple",
            "Normal",
            "DDIM",
            "Beta",
            "Turbo",
            "Align Your Steps GITS",
            "Align Your Steps 11",
            "Align Your Steps 32",
            "Other",
        ]

        enum_values = [scheduler.value for scheduler in SchedulerType]

        assert len(enum_values) == len(expected_values)
        for expected_value in expected_values:
            assert expected_value in enum_values


class TestTechniqueType:
    """Test cases for TechniqueType enum."""

    def test_EnumValues_ShouldHaveCorrectStringValues(self):
        """Test that TechniqueType enum values have correct string representations."""
        assert TechniqueType.TEXT_TO_IMAGE.value == "txt2img"
        assert TechniqueType.IMAGE_TO_IMAGE.value == "img2img"
        assert TechniqueType.INPAINTING.value == "inpainting"
        assert TechniqueType.OTHER.value == "other"

    def test_StrMethod_ShouldReturnValue(self):
        """Test that __str__ method returns enum value."""
        assert str(TechniqueType.TEXT_TO_IMAGE) == "txt2img"
        assert str(TechniqueType.CONTROL_NET) == "controlnet"

    def test_AllEnumValues_ShouldBeAccessible(self):
        """Test that all enum values are accessible."""
        expected_values = [
            "txt2img",
            "img2img",
            "inpainting",
            "outpainting",
            "hires_fix",
            "adetailer",
            "controlnet",
            "tiled_upscale",
            "cfg_fix",
            "dynamic_prompting",
            "regional_prompting",
            "other",
        ]

        enum_values = [technique.value for technique in TechniqueType]

        assert len(enum_values) == len(expected_values)
        for expected_value in expected_values:
            assert expected_value in enum_values


class TestImageRepositoryType:
    """Test cases for ImageRepositoryType enum."""

    def test_EnumValues_ShouldHaveCorrectStringValues(self):
        """Test that ImageRepositoryType enum values have correct string representations."""
        assert ImageRepositoryType.DISK.value == "Disk"
        assert ImageRepositoryType.S3.value == "S3"
        assert ImageRepositoryType.DEVIANTART.value == "DeviantArt"

    def test_StrMethod_ShouldReturnValue(self):
        """Test that __str__ method returns enum value."""
        assert str(ImageRepositoryType.DISK) == "Disk"
        assert str(ImageRepositoryType.S3) == "S3"

    def test_AllEnumValues_ShouldBeAccessible(self):
        """Test that all enum values are accessible."""
        expected_values = ["Disk", "S3", "DeviantArt"]

        enum_values = [repo_type.value for repo_type in ImageRepositoryType]

        assert len(enum_values) == len(expected_values)
        for expected_value in expected_values:
            assert expected_value in enum_values
