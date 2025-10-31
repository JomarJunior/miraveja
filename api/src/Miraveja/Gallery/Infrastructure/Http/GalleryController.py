from typing import Optional
from fastapi.exceptions import HTTPException
from Miraveja.Gallery.Application.FindImageMetadataById import (
    FindImageMetadataByIdHandler,
)
from Miraveja.Gallery.Application.GetPresignedPostUrl import GetPresignedPostUrlCommand, GetPresignedPostUrlHandler
from Miraveja.Gallery.Application.ListAllImageMetadatas import (
    ListAllImageMetadatasCommand,
    ListAllImageMetadatasHandler,
)
from Miraveja.Gallery.Application.RegisterImageMetadata import (
    RegisterImageMetadataCommand,
    RegisterImageMetadataHandler,
)
from Miraveja.Gallery.Application.UpdateImageMetadata import UpdateImageMetadataCommand, UpdateImageMetadataHandler
from Miraveja.Shared.Errors.Models import DomainException
from Miraveja.Shared.Identifiers.Models import ImageMetadataId
from Miraveja.Shared.Keycloak.Domain.Models import KeycloakUser
from Miraveja.Shared.Logging.Interfaces import ILogger
from Miraveja.Shared.Utils.Types.Handler import HandlerResponse


class GalleryController:
    def __init__(
        self,
        listAllImageMetadatasHandler: ListAllImageMetadatasHandler,
        findImageMetadataByIdHandler: FindImageMetadataByIdHandler,
        registerImageMetadataHandler: RegisterImageMetadataHandler,
        updateImageMetadataHandler: UpdateImageMetadataHandler,
        getPresignedPostUrlHandler: GetPresignedPostUrlHandler,
        logger: ILogger,
    ):
        self._listAllImageMetadatasHandler = listAllImageMetadatasHandler
        self._findImageMetadataByIdHandler = findImageMetadataByIdHandler
        self._registerImageMetadataHandler = registerImageMetadataHandler
        self._updateImageMetadataHandler = updateImageMetadataHandler
        self._getPresignedPostUrlHandler = getPresignedPostUrlHandler
        self._logger = logger

    async def ListAllImageMetadatas(self, command: Optional[ListAllImageMetadatasCommand] = None) -> HandlerResponse:
        try:
            if command is None:
                command = ListAllImageMetadatasCommand()
            return self._listAllImageMetadatasHandler.Handle(command)
        except DomainException as domainException:
            self._logger.Error(f"{str(domainException)}")
            raise HTTPException(status_code=400, detail=str(domainException)) from domainException
        except Exception as exception:
            self._logger.Error(f"Unexpected error during listing image metadatas: {str(exception)}")
            raise HTTPException(status_code=500, detail="Internal server error") from exception

    async def FindImageMetadataById(self, imageMetadataId: ImageMetadataId) -> HandlerResponse:
        try:
            imageMetadata: Optional[HandlerResponse] = self._findImageMetadataByIdHandler.Handle(imageMetadataId)
        except DomainException as domainException:
            self._logger.Error(f"{str(domainException)}")
            raise HTTPException(status_code=400, detail=str(domainException)) from domainException

        except Exception as exception:
            self._logger.Error(f"Unexpected error during finding image metadata by ID: {str(exception)}")
            raise HTTPException(status_code=500, detail="Internal server error") from exception

        if imageMetadata is None:
            raise HTTPException(status_code=404, detail="Image metadata not found")
        return imageMetadata

    async def RegisterImageMetadata(
        self, command: RegisterImageMetadataCommand, agent: KeycloakUser
    ) -> HandlerResponse:
        try:
            imageMetadataId = await self._registerImageMetadataHandler.Handle(command)
            self._logger.Info(f"Image metadata registered successfully: {imageMetadataId}")
            self._logger.Info(f"Registered by agent: {agent.id}")
            return {"message": "Image metadata registered successfully"}

        except DomainException as domainException:
            self._logger.Error(f"{str(domainException)}")
            raise HTTPException(status_code=400, detail=str(domainException)) from domainException
        except Exception as exception:
            self._logger.Error(f"Unexpected error during registering image metadata: {str(exception)}")
            raise HTTPException(status_code=500, detail="Internal server error") from exception

    async def UpdateImageMetadata(
        self, imageMetadataId: ImageMetadataId, command: UpdateImageMetadataCommand, agent: KeycloakUser
    ) -> HandlerResponse:
        try:
            await self._updateImageMetadataHandler.Handle(imageMetadataId, command)
            self._logger.Info(f"Image metadata updated successfully: {imageMetadataId.id}")
            self._logger.Info(f"Updated by agent: {agent.id}")
            return {"message": "Image metadata updated successfully"}

        except DomainException as domainException:
            self._logger.Error(f"{str(domainException)}")
            raise HTTPException(status_code=400, detail=str(domainException)) from domainException
        except Exception as exception:
            self._logger.Error(f"Unexpected error during updating image metadata: {str(exception)}")
            raise HTTPException(status_code=500, detail="Internal server error") from exception

    async def GetPresignedPostUrl(self, command: GetPresignedPostUrlCommand, agent: KeycloakUser) -> HandlerResponse:
        return await self._getPresignedPostUrlHandler.Handle(command, agent)
