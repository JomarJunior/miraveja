from typing import Any, List, Optional, Type
from pydantic import BaseModel, Field, field_validator

from MiravejaCore.Gallery.Application.FindLoraMetadataByHash import FindLoraMetadataByHashHandler
from MiravejaCore.Gallery.Application.RegisterLoraMetadata import (
    RegisterLoraMetadataCommand,
    RegisterLoraMetadataHandler,
)
from MiravejaCore.Gallery.Domain.Enums import SamplerType, SchedulerType, TechniqueType
from MiravejaCore.Gallery.Domain.Interfaces import IGenerationMetadataRepository
from MiravejaCore.Gallery.Domain.Models import GenerationMetadata, LoraMetadata, Size
from MiravejaCore.Shared.Identifiers.Models import GenerationMetadataId, ImageMetadataId, LoraMetadataId
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.DatabaseManager.Domain.Interfaces import IDatabaseManagerFactory


class RegisterGenerationMetadataCommand(BaseModel):
    prompt: str = Field(..., description="The prompt used for generation", max_length=2000)
    negativePrompt: Optional[str] = Field(None, description="The negative prompt used for generation", max_length=2000)
    seed: Optional[str] = Field(None, description="The seed used for generation")
    model: Optional[str] = Field(None, description="The hash of the model used for generation")
    sampler: Optional[SamplerType] = Field(None, description="The sampler used for generation")
    scheduler: Optional[SchedulerType] = Field(None, description="The scheduler used for generation")
    steps: Optional[int] = Field(None, description="The number of steps used for generation")
    cfgScale: Optional[float] = Field(None, description="The CFG scale used for generation")
    size: Optional[Size] = Field(None, description="The size used for generation")
    loras: Optional[List[RegisterLoraMetadataCommand]] = Field(None, description="List of LoRAs used for generation")
    techniques: Optional[List[TechniqueType]] = Field(None, description="List of techniques used for generation")

    @field_validator("techniques", mode="before")
    def ValidateTechniques(cls, value: Any) -> Optional[List[TechniqueType]]:
        if value is None:
            return value
        if isinstance(value, str):
            # Convert comma-separated string to list of TechniqueType
            return [TechniqueType(v) for v in value.split(",")]

        return value


class RegisterGenerationMetadataHandler:
    def __init__(
        self,
        databaseUOWFactory: IDatabaseManagerFactory,
        tGenerationMetadataRepository: Type[IGenerationMetadataRepository],
        findLoraMetadataByHashHandler: FindLoraMetadataByHashHandler,
        registerLoraMetadataHandler: RegisterLoraMetadataHandler,
        logger: ILogger,
    ):
        self.databaseUOWFactory = databaseUOWFactory
        self.tGenerationMetadataRepository = tGenerationMetadataRepository
        self.findLoraMetadataByHashHandler = findLoraMetadataByHashHandler
        self.registerLoraMetadataHandler = registerLoraMetadataHandler
        self.logger = logger

    def Handle(self, imageId: ImageMetadataId, command: RegisterGenerationMetadataCommand) -> int:
        self.logger.Info(f"Registering generation metadata with command: {command.model_dump_json(indent=4)}")

        with self.databaseUOWFactory.Create() as databaseManager:
            generationMetadataId: GenerationMetadataId = databaseManager.GetRepository(
                self.tGenerationMetadataRepository
            ).GenerateNewId()

            self.logger.Debug(f"Creating generation metadata entity with ID: {generationMetadataId.id}")

            loraMetadatas: List[LoraMetadata] = []
            if command.loras:
                for lora in command.loras:
                    existingLora = self.findLoraMetadataByHashHandler.Handle(lora.hash)
                    if existingLora is not None:
                        self.logger.Debug(f"LoRA with hash {lora.hash} already exists with ID {existingLora['id']}")
                        loraMetadatas.append(LoraMetadata.model_validate(existingLora))
                    else:
                        newLoraId = self.registerLoraMetadataHandler.Handle(lora)
                        self.logger.Debug(f"Registered new LoRA with hash {lora.hash} and ID {newLoraId}")
                        loraMetadatas.append(LoraMetadata(id=LoraMetadataId(id=newLoraId), **lora.model_dump()))

            generationMetadata = GenerationMetadata.Register(
                id=generationMetadataId,
                imageId=imageId,
                prompt=command.prompt,
                negativePrompt=command.negativePrompt,
                seed=command.seed,
                model=command.model,
                sampler=command.sampler,
                scheduler=command.scheduler,
                steps=command.steps,
                cfgScale=command.cfgScale,
                size=command.size,
                loras=loraMetadatas,
                techniques=command.techniques,
            )

            databaseManager.GetRepository(self.tGenerationMetadataRepository).Save(generationMetadata)
            databaseManager.Commit()

        self.logger.Info(f"Generation metadata registered with ID: {generationMetadataId.id}")

        return generationMetadataId.id
