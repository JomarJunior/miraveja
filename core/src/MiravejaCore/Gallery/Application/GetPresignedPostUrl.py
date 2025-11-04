from pydantic import BaseModel, Field

from MiravejaCore.Gallery.Domain.Interfaces import IImageContentRepository
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Keycloak.Domain.Models import KeycloakUser
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Shared.Storage.Domain.Enums import MimeType
from MiravejaCore.Shared.Storage.Domain.Services import SignedUrlService
from MiravejaCore.Shared.Utils.Types.Handler import HandlerResponse


class GetPresignedPostUrlCommand(BaseModel):
    filename: str = Field(..., description="The name of the file to be uploaded")
    mimeType: MimeType = Field(..., description="The MIME type of the file to be uploaded")
    size: int = Field(..., description="The size of the file to be uploaded in bytes")


class GetPresignedPostUrlHandler:
    def __init__(
        self,
        imageContentRepository: IImageContentRepository,
        signedUrlService: SignedUrlService,
        logger: ILogger,
    ):
        self.imageContentRepository = imageContentRepository
        self.signedUrlService = signedUrlService
        self.logger = logger

    async def Handle(self, command: GetPresignedPostUrlCommand, agent: KeycloakUser) -> HandlerResponse:
        try:
            key: str = f"{agent.id}/gallery/{command.filename}"

            presignedPostUrl = await self.imageContentRepository.GetPresignedPostUrl(
                key=key,
                ownerId=MemberId(id=agent.id),
            )

            # Convert the internal docker URL to a relative URL for external access
            relativeUrl = self.signedUrlService.GetRelativeUrl(presignedPostUrl["url"])
            presignedPostUrl["url"] = relativeUrl

            return presignedPostUrl
        except Exception as exception:
            self.logger.Error(f"Unexpected error during getting presigned post URL: {str(exception)}")
            raise exception
