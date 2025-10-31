from typing import Type, Optional

from pydantic import BaseModel, Field

from Miraveja.Gallery.Application.RegisterGenerationMetadata import (
    RegisterGenerationMetadataCommand,
    RegisterGenerationMetadataHandler,
)
from Miraveja.Gallery.Domain.Enums import ImageRepositoryType
from Miraveja.Gallery.Domain.Interfaces import IImageContentRepository, IImageMetadataRepository
from Miraveja.Gallery.Domain.Models import ImageMetadata, Size
from Miraveja.Gallery.Domain.Exceptions import (
    ImageContentNotFoundException,
    ImageMetadataUriAlreadyExistsException,
)
from Miraveja.Shared.Events.Application.EventDispatcher import EventDispatcher
from Miraveja.Shared.Identifiers.Models import ImageMetadataId, MemberId, VectorId
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.UnitOfWork.Domain.Interfaces import IUnitOfWorkFactory


class RegisterImageMetadataCommand(BaseModel):
    ownerId: str = Field(..., description="Unique identifier of the member who owns the image")
    title: str = Field(..., min_length=1, max_length=200, description="Title of the image")
    subtitle: str = Field(..., min_length=0, max_length=200, description="Subtitle of the image")
    description: Optional[str] = Field(None, max_length=2000, description="Description of the image")
    width: int = Field(..., gt=0, description="Width of the image in pixels")
    height: int = Field(..., gt=0, description="Height of the image in pixels")
    repositoryType: ImageRepositoryType = Field(..., description="The repository type where the image is stored")
    uri: str = Field(..., min_length=1, max_length=500, description="The URI of the image")
    isAiGenerated: bool = Field(..., description="Flag indicating if the image was AI-generated")
    generationMetadata: Optional[RegisterGenerationMetadataCommand] = Field(
        None, description="Metadata related to the image generation"
    )
    vectorId: Optional[VectorId] = Field(None, description="Identifier linking to the associated vector data")


class RegisterImageMetadataHandler:
    def __init__(
        self,
        databaseUOWFactory: IUnitOfWorkFactory,
        tImageMetadataRepository: Type[IImageMetadataRepository],
        registerGenerationMetadataHandler: RegisterGenerationMetadataHandler,
        imageContentRepository: IImageContentRepository,
        eventDispatcher: EventDispatcher,
        logger: ILogger,
    ):
        self._databaseUOWFactory = databaseUOWFactory
        self._tImageMetadataRepository = tImageMetadataRepository
        self._registerGenerationMetadataHandler = registerGenerationMetadataHandler
        self._imageContentRepository = imageContentRepository
        self._eventDispatcher = eventDispatcher
        self._logger = logger

    async def Handle(self, command: RegisterImageMetadataCommand) -> int:
        self._logger.Info(f"Registering image metadata with command: {command.model_dump_json(indent=4)}")

        with self._databaseUOWFactory.Create() as unitOfWork:
            repository = unitOfWork.GetRepository(self._tImageMetadataRepository)

            # Check for existing image metadata with the same URI
            existingImageMetadata = repository.FindByUri(command.uri)
            if existingImageMetadata:
                self._logger.Warning(f"Image metadata with URI {command.uri} already exists.")
                raise ImageMetadataUriAlreadyExistsException(command.uri)

            if command.repositoryType == ImageRepositoryType.S3:
                # Check if the image was indeed uploaded to storage
                if not await self._imageContentRepository.Exists(command.uri):
                    self._logger.Warning(f"Image content with URI {command.uri} does not exist.")
                    raise ImageContentNotFoundException(command.uri)
                # Check if the image was uploaded by the claimed owner
                if not await self._imageContentRepository.IsOwnedBy(command.uri, MemberId(id=command.ownerId)):
                    self._logger.Warning(
                        f"Image content with URI {command.uri} is not owned by member ID {command.ownerId}."
                    )
                    raise ImageContentNotFoundException(command.uri)
            # @todo Handle other repository types (e.g., DevianArt, etc.)

            imageMetadataId: ImageMetadataId = repository.GenerateNewId()

            self._logger.Debug(f"Creating image metadata entity with ID: {imageMetadataId.id}")

            ownerId = MemberId(id=command.ownerId)
            size = Size(width=command.width, height=command.height)

            imageMetadata = ImageMetadata.Register(
                id=imageMetadataId,
                ownerId=ownerId,
                title=command.title,
                subtitle=command.subtitle,
                description=command.description,
                size=size,
                repositoryType=command.repositoryType,
                uri=command.uri,
                isAiGenerated=command.isAiGenerated,
                generationMetadata=None,
                vectorId=command.vectorId,
            )

            repository.Save(imageMetadata)
            unitOfWork.Commit()

            # Handle generation metadata if the image is AI-generated
            if command.isAiGenerated and command.generationMetadata:
                self._registerGenerationMetadataHandler.Handle(
                    imageId=imageMetadataId, command=command.generationMetadata
                )

            unitOfWork.Commit()
        self._logger.Info(f"Image metadata registered with ID: {imageMetadataId.id}")

        await self._eventDispatcher.DispatchAll(imageMetadata.ReleaseEvents())

        return imageMetadataId.id
