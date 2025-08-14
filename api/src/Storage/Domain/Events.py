"""
Events for Storage Context.
To avoid circular dependencies, we will not type hint the model classes.
"""

from src.Core.Events.Base import BaseEvent
from datetime import datetime

class ImageRegisteredEvent(BaseEvent):
    """
    Event triggered when a new image is registered to the database.
    """
    def __init__(self, image):
        super().__init__(self.__class__.__name__)
        self.image = image
        self.timestamp = datetime.now()

class ImageUpdatedEvent(BaseEvent):
    """
    Event triggered when an existing image is updated in the database.
    """
    def __init__(self, new_image, old_image):
        super().__init__(self.__class__.__name__)
        self.new_image = new_image
        self.old_image = old_image
        self.timestamp = datetime.now()

class ProviderRegisteredEvent(BaseEvent):
    """
    Event triggered when a new provider is registered to the database.
    """
    def __init__(self, provider):
        super().__init__(self.__class__.__name__)
        self.provider = provider
        self.timestamp = datetime.now()

class ProviderUpdatedEvent(BaseEvent):
    """
    Event triggered when an existing provider is updated in the database.
    """
    def __init__(self, new_provider, old_provider):
        super().__init__(self.__class__.__name__)
        self.new_provider = new_provider
        self.old_provider = old_provider
        self.timestamp = datetime.now()

class ImageContentDownloadedEvent(BaseEvent):
    """
    Event triggered when an image content is downloaded from the file system.
    """
    def __init__(self, content):
        super().__init__(self.__class__.__name__)
        self.content = content
        self.timestamp = datetime.now()

class ImageContentUploadedEvent(BaseEvent):
    """
    Event triggered when an image content is uploaded to the file system.
    """
    def __init__(self, content):
        super().__init__(self.__class__.__name__)
        self.content = content
        self.timestamp = datetime.now()
