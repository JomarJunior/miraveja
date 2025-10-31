from typing import Optional
from fastapi import APIRouter, Depends

from Miraveja.Gallery.Application.GetPresignedPostUrl import GetPresignedPostUrlCommand
from Miraveja.Gallery.Application.ListAllImageMetadatas import ListAllImageMetadatasCommand
from Miraveja.Gallery.Application.RegisterImageMetadata import RegisterImageMetadataCommand
from Miraveja.Gallery.Application.UpdateImageMetadata import UpdateImageMetadataCommand
from Miraveja.Gallery.Infrastructure.Http.GalleryController import GalleryController
from Miraveja.Member.Application.ListAllMembers import HandlerResponse
from Miraveja.Shared.Identifiers.Models import ImageMetadataId
from Miraveja.Shared.Keycloak.Domain.Models import KeycloakUser
from Miraveja.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider


BASE_ROUTE = "/gallery"


class GalleryRoutes:
    @staticmethod
    def RegisterRoutes(
        router: APIRouter, controller: GalleryController, keycloakDependencyProvider: KeycloakDependencyProvider
    ):
        @router.post(f"{BASE_ROUTE}/images/", response_model=HandlerResponse)
        async def RegisterImageMetadataRoute(
            command: RegisterImageMetadataCommand,
            agent: KeycloakUser = Depends(keycloakDependencyProvider.RequireAuthentication),
        ):
            return await controller.RegisterImageMetadata(command, agent)

        @router.put(f"{BASE_ROUTE}/images/{{imageMetadataId}}", response_model=HandlerResponse)
        async def UpdateImageMetadataRoute(
            imageMetadataId: int,
            command: UpdateImageMetadataCommand,
            agent: KeycloakUser = Depends(keycloakDependencyProvider.RequireAuthentication),
        ):
            return await controller.UpdateImageMetadata(ImageMetadataId(id=imageMetadataId), command, agent)

        @router.get(f"{BASE_ROUTE}/images/", response_model=HandlerResponse)
        async def ListAllImageMetadatasRoute(command: Optional[ListAllImageMetadatasCommand] = None):
            return await controller.ListAllImageMetadatas(command)

        @router.get(f"{BASE_ROUTE}/images/{{imageMetadataId}}", response_model=HandlerResponse)
        async def FindImageMetadataByIdRoute(imageMetadataId: int):
            return await controller.FindImageMetadataById(ImageMetadataId(id=imageMetadataId))

        @router.post(f"{BASE_ROUTE}/images/presign", response_model=HandlerResponse)
        async def GetPresignedPostUrlRoute(
            command: GetPresignedPostUrlCommand,
            agent: KeycloakUser = Depends(keycloakDependencyProvider.RequireAuthentication),
        ):
            return await controller.GetPresignedPostUrl(command, agent)
