"""
Repositories implementations
"""

from src.Storage.Domain.Interfaces import IImageRepository, IProviderRepository, IEncryptionService, IImageContentRepository
from src.Storage.Domain.Models import Image, ImageContent, Provider
from src.Storage.Domain.Enums import ImageFormatEnum
from sqlalchemy.orm import Session as DatabaseSession
from typing import List
import os
from random import randbytes

class SqlImageRepository(IImageRepository):
    def __init__(self, database_session: DatabaseSession):
        self.database_session = database_session

    def list_all(self, sort_by: str, sort_order: str, search_filter: dict, limit: int) -> List[Image]:
        query = self.database_session.query(Image)

        # Apply search filters
        if search_filter:
            for key, value in search_filter.items():
                query = query.filter(getattr(Image, key).ilike(f"%{value}%"))

        # Apply sorting
        if sort_by:
            query = query.order_by(getattr(Image, sort_by).desc() if sort_order == "desc" else getattr(Image, sort_by))

        # Apply limit
        query = query.limit(limit)

        images = query.all()
        return images
    
    def find_by_id(self, image_id: int) -> Image:
        return self.database_session.query(Image).filter(Image.id == image_id).first()

    def save(self, image: Image) -> None:
        """
            This method saves an image to the database.
            If the image is new, it will be added to the session.
            If the image already exists, it will be updated.
        """
        existing_image = self.find_by_id(image.id)
        if existing_image:
            existing_image.update(image)
        else:
            self.database_session.add(image)
        try:
            self.database_session.commit()
        except Exception as exception:
            self.database_session.rollback()
            raise exception

class SqlProviderRepository(IProviderRepository):
    def __init__(self, database_session: DatabaseSession):
        self.database_session = database_session

    def list_all(self, sort_by: str, sort_order: str, search_filter: dict, limit: int) -> List[Provider]:
        query = self.database_session.query(Provider)

        # Apply search filters
        if search_filter:
            for key, value in search_filter.items():
                query = query.filter(getattr(Provider, key).ilike(f"%{value}%"))

        # Apply sorting
        if sort_by:
            query = query.order_by(getattr(Provider, sort_by).desc() if sort_order == "desc" else getattr(Provider, sort_by))

        # Apply limit
        query = query.limit(limit)

        providers = query.all()
        return providers
    
    def find_by_id(self, provider_id: int) -> Provider:
        return self.database_session.query(Provider).filter(Provider.id == provider_id).first()

    def save(self, provider: Provider) -> None:
        """
            This method saves a provider to the database.
            If the provider is new, it will be added to the session.
            If the provider already exists, it will be updated.
        """
        existing_provider = self.find_by_id(provider.id)
        if existing_provider:
            existing_provider.update(provider)
        else:
            self.database_session.add(provider)
        try:
            self.database_session.commit()
        except Exception as exception:
            self.database_session.rollback()
            raise exception

class FilesystemImageContentRepository(IImageContentRepository):
    def __init__(self, encryption_service: IEncryptionService, main_path: str, final_extension: str):
        self.encryption_service = encryption_service
        self.main_path = f"{main_path}/images"
        self.final_extension = final_extension

    def find_by_uri(self, uri: str) -> ImageContent:
        # We store the encrypted content with a specific file extension
        path = self.build_real_path(uri)

        if not os.path.exists(path):
            raise KeyError(f"Image content with URI {uri} not found")
        with open(path, "rb") as file:
            content = file.read()

        decrypted_content = self.encryption_service.decrypt(content)
        return ImageContent(uri=uri, content=decrypted_content)

    def save(self, image_content: ImageContent) -> None:
        # We store the encrypted content with a specific file extension
        path = self.build_real_path(image_content.uri)

        encrypted_content = self.encryption_service.encrypt(image_content.content)
        with open(path, "wb") as file:
            file.write(encrypted_content)
    
    def get_next_available_uri(self, extension: str) -> str:
        random_bytes: str = randbytes(16).hex()
        return f"{self.main_path}/{random_bytes}.{extension}"

    def build_real_path(self, uri: str) -> str:
        return f"{uri.split('.')[0]}.{self.final_extension}"