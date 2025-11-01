from typing import Optional
from fastapi import APIRouter, Depends

from MiravejaCore.Gallery.Application.GetPresignedPostUrl import GetPresignedPostUrlCommand
from MiravejaCore.Gallery.Application.ListAllImageMetadatas import ListAllImageMetadatasCommand
from MiravejaCore.Gallery.Application.RegisterImageMetadata import RegisterImageMetadataCommand
from MiravejaCore.Gallery.Application.UpdateImageMetadata import UpdateImageMetadataCommand
from MiravejaApi.Gallery.Infrastructure.Http.GalleryController import GalleryController
from MiravejaCore.Member.Application.ListAllMembers import HandlerResponse
from MiravejaCore.Shared.Identifiers.Models import ImageMetadataId
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Keycloak.Infrastructure.Http.DependencyProvider import KeycloakDependencyProvider


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
