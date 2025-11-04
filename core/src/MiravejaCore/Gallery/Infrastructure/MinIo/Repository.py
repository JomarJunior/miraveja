from typing import Any, Dict
from botocore.client import BaseClient as Boto3Client
from MiravejaCore.Shared.Storage.Domain.Configuration import MinIoConfig
from MiravejaCore.Gallery.Domain.Interfaces import IImageContentRepository
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class MinIoImageContentRepository(IImageContentRepository):
    def __init__(self, boto3Client: Boto3Client, config: MinIoConfig, logger: ILogger) -> None:
        self._boto3Client = boto3Client
        self._config = config
        self._logger = logger
        self._Initialize()

    def _Initialize(self) -> None:
        # Ensure the bucket exists
        existingBuckets = self._boto3Client.list_buckets()
        bucketNames = [bucket["Name"] for bucket in existingBuckets.get("Buckets", [])]
        if self._config.bucketName not in bucketNames:
            self._logger.Info(f"Creating bucket {self._config.bucketName}")
            self._boto3Client.create_bucket(
                Bucket=self._config.bucketName,
                ObjectLockEnabledForBucket=True,
            )
        else:
            self._logger.Info(f"Bucket {self._config.bucketName} already exists")

    def _GetImageKey(self, imageUri: str) -> str:
        # the image uri is f"{config.outsideEndpoint}/{config.bucketName}/{imageKey}"
        return imageUri.replace(f"{self._config.outsideEndpoint.rstrip('/')}/{self._config.bucketName}/", "")

    async def GetPresignedGetUrl(self, key: str) -> str:
        self._logger.Info(f"Generating presigned GET URL for {key}")
        try:
            presignedUrl = self._boto3Client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._config.bucketName, "Key": key},
                ExpiresIn=self._config.presignedUrlExpirationSeconds,
            )
            return presignedUrl
        except Exception as e:
            self._logger.Error(f"Error generating presigned GET URL: {e}")
            raise e

    async def GetPresignedPostUrl(self, key: str, ownerId: MemberId) -> Dict[str, Any]:
        self._logger.Info(f"Generating presigned POST URL for {key}")
        try:
            presignedPost = self._boto3Client.generate_presigned_post(
                Bucket=self._config.bucketName,
                Key=key,
                Fields={
                    "acl": "private",
                    "x-amz-meta-owner-id": str(ownerId.id),
                },
                Conditions=[
                    ["content-length-range", 0, self._config.maxFileSizeBytes],
                    {"acl": "private"},
                    {"x-amz-meta-owner-id": str(ownerId.id)},
                ],
                ExpiresIn=self._config.presignedUrlExpirationSeconds,
            )
            return presignedPost
        except Exception as e:
            self._logger.Error(f"Error generating presigned POST URL: {e}")
            raise e

    async def GetMetadata(self, imageUri: str) -> dict:
        key = self._GetImageKey(imageUri)
        self._logger.Info(f"Fetching metadata for {key}")
        try:
            response = self._boto3Client.head_object(Bucket=self._config.bucketName, Key=key)
            return response.get("Metadata", {})
        except self._boto3Client.exceptions.NoSuchKey:
            self._logger.Warning(f"Object {key} not found in bucket {self._config.bucketName}")
            return {}
        except Exception as e:
            self._logger.Error(f"Error fetching metadata for {key}: {e}")
            raise e

    async def Delete(self, imageUri: str) -> None:
        key = self._GetImageKey(imageUri)
        self._logger.Info(f"Deleting object {key} from bucket {self._config.bucketName}")
        try:
            self._boto3Client.delete_object(Bucket=self._config.bucketName, Key=key)
            self._logger.Info(f"Successfully deleted {key}")
        except Exception as e:
            self._logger.Error(f"Error deleting object {key}: {e}")
            raise e

    async def Exists(self, imageUri: str) -> bool:
        key = self._GetImageKey(imageUri)
        self._logger.Info(f"Checking existence of object {key} in bucket {self._config.bucketName}")
        try:
            self._boto3Client.head_object(Bucket=self._config.bucketName, Key=key)
            self._logger.Info(f"Object {key} exists")
            return True
        except Exception as e:
            self._logger.Error(f"Error checking existence of object {key}: {e}")
            if "Not Found" in str(e):
                self._logger.Info(f"Object {key} does not exist")
                return False
            raise e

    async def IsOwnedBy(self, imageUri: str, ownerId: MemberId) -> bool:
        self._logger.Info(f"Checking ownership of object {imageUri} by member ID {ownerId.id}")
        try:
            metadata = await self.GetMetadata(imageUri)
            actualOwnerId = metadata.get("owner-id")
            if actualOwnerId == str(ownerId.id):
                self._logger.Info(f"Object {imageUri} is owned by member ID {ownerId.id}")
                return True

            self._logger.Warning(f"Object {imageUri} is not owned by member ID {ownerId.id}")
            return False
        except Exception as e:
            self._logger.Error(f"Error checking ownership of object {imageUri}: {e}")
            raise e
