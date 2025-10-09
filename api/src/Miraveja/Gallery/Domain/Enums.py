from enum import Enum


class SamplerType(str, Enum):
    """Enumeration of different sampler types."""

    DPMPP_2M = "DPM++_2M"
    DPMPP_SDE = "DPM++_SDE"
    DPMPP_2M_SDE = "DPM++_2M_SDE"
    DPMPP_2M_SDE_HEUN = "DPM++_2M_SDE_Heun"
    DPMPP_2S_A = "DPM++_2S_a"
    DPMPP_3M_SDE = "DPM++_3M_SDE"
    EULER_A = "Euler_a"
    EULER = "Euler"
    LMS = "LMS"
    HEUN = "Heun"
    DPM2 = "DPM2"
    DPM2_A = "DPM2_a"
    DPM_FAST = "DPM_fast"
    DPM_ADAPTIVE = "DPM_adaptive"
    RESTART = "Restart"
    HEUNPP2 = "HeunPP2"
    IPNDM = "IPNDM"
    IPNDM_V = "IPNDM_V"
    DEIS = "DEIS"
    DDIM = "DDIM"
    DDIM_CFGPP = "DDIM_CFG++"
    PLMS = "PLMS"
    UNIPC = "UniPC"
    LCM = "LCM"
    DDPM = "DDPM"
    OTHER = "Other"

    def __str__(self) -> str:
        return self.value


class SchedulerType(str, Enum):
    """Enumeration of different scheduler types."""

    AUTOMATIC = "Automatic"
    UNIFORM = "Uniform"
    KARRAS = "Karras"
    EXPONENTIAL = "Exponential"
    POLYEXPONENTIAL = "Polyexponential"
    SGM_UNIFORM = "SGM Uniform"
    KL_OPTIMAL = "KL Optimal"
    ALIGN_YOUR_STEPS = "Align Your Steps"
    SIMPLE = "Simple"
    NORMAL = "Normal"
    DDIM = "DDIM"
    BETA = "Beta"
    TURBO = "Turbo"
    ALIGN_YOUR_STEPS_GITS = "Align Your Steps GITS"
    ALIGN_YOUR_STEPS_11 = "Align Your Steps 11"
    ALIGN_YOUR_STEPS_32 = "Align Your Steps 32"
    OTHER = "Other"

    def __str__(self) -> str:
        return self.value


class TechniqueType(str, Enum):
    """Enumeration of different technique types."""

    TEXT_TO_IMAGE = "txt2img"
    IMAGE_TO_IMAGE = "img2img"
    INPAINTING = "inpainting"
    OUTPAINTING = "outpainting"
    HIRES_FIX = "hires_fix"
    ADETAILER = "adetailer"
    CONTROL_NET = "controlnet"
    TILED_UPSCALE = "tiled_upscale"
    CFG_FIX = "cfg_fix"
    DYNAMIC_PROMPTING = "dynamic_prompting"
    REGIONAL_PROMPTING = "regional_prompting"
    OTHER = "other"

    def __str__(self) -> str:
        return self.value


class ImageRepositoryType(str, Enum):
    """
    Enumeration of different location types where images can be stored.
    """

    DISK = "Disk"
    S3 = "S3"
    DEVIANTART = "DeviantArt"

    def __str__(self) -> str:
        return self.value
