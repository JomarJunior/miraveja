"""
Commands to be processed by use case handlers
"""

from typing import Dict, Any, Type

# Base
class ListAllCommand:
    def __init__(self, sort_by: str, sort_order: str, search_filter: Dict[str, Any], limit: int):
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.search_filter = search_filter
        self.limit = limit

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            sort_by=data.get("sort_by", ""),
            sort_order=data.get("sort_order", ""),
            search_filter=data.get("search_filter", {}),
            limit=data.get("limit", 100)
        )
    
    def __str__(self):
        return f"{self.__class__.__name__}(sort_by={self.sort_by}, sort_order={self.sort_order}, search_filter={self.search_filter}, limit={self.limit})"

class FindCommand:
    def __init__(self, id: int):
        self.id = id

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            id=data.get("id", 0)
        )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id})"

# Images
class RegisterImageCommand:
    def __init__(self, image_uri: str, image_metadata: dict, provider_id: int):
        if not image_uri:
            raise ValueError("image_uri is required")
        if not image_metadata:
            raise ValueError("image_metadata is required")
        if provider_id <= 0:
            raise ValueError("provider_id must be positive")

        self.image_uri = image_uri
        self.image_metadata = image_metadata
        self.provider_id = provider_id

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RegisterImageCommand':
        return RegisterImageCommand(
            image_uri=data.get("image_uri", ""),
            image_metadata=data.get("image_metadata", {}),
            provider_id=data.get("provider_id", 0)
        )

    def __str__(self):
        return f"{self.__class__.__name__}(image_uri={self.image_uri}, image_metadata={self.image_metadata}, provider_id={self.provider_id})"

class ListAllImagesCommand(ListAllCommand):
    pass

class FindImageByIdCommand(FindCommand):
    pass

# Providers
class RegisterProviderCommand:
    def __init__(self, name: str):
        if not name:
            raise ValueError("name is required")
        self.name = name

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RegisterProviderCommand':
        return RegisterProviderCommand(
            name=data.get("name", "")
        )
    
    def __str__(self):
        return f"{self.__class__.__name__}(name={self.name})"

class ListAllProvidersCommand(ListAllCommand):
    pass

class FindProviderByIdCommand(FindCommand):
    pass

# Image Content
class DownloadImageContentCommand:
    def __init__(self, id: int):
        if id <= 0:
            raise ValueError("id must be positive")
        self.id = id

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DownloadImageContentCommand':
        return DownloadImageContentCommand(
            id=data.get("id", 0)
        )

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id})"

class UploadImageContentCommand:
    def __init__(self, content: str):
        if not content or not content.strip():
            raise ValueError("content is required")
        self.content = content.strip()

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'UploadImageContentCommand':
        return UploadImageContentCommand(
            content=data.get("content", "")
        )

    def __str__(self):
        return f"{self.__class__.__name__}(content_length={len(self.content)})"