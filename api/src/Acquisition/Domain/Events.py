"""
Image events for the acquisition domain.
To avoid circular imports, we do not import the models directly.
"""

from typing import Any, List
from src.Core.Events.Base import BaseEvent
from datetime import datetime

class ImageCreatedEvent(BaseEvent):
    """
    Event triggered when a new image is created.
    """
    def __init__(self, image):
        super().__init__(self.__class__.__name__)
        self.image = image
        self.occurred_at = datetime.now()

class ImageDownloadedEvent(BaseEvent):
    """
    Event triggered when an image is downloaded.
    """
    def __init__(self, image_content):
        super().__init__(self.__class__.__name__)
        self.image_content = image_content
        self.occurred_at = datetime.now()

class ManyImagesAcquiredEvent(BaseEvent):
    """
    Event triggered when multiple images are acquired.
    """
    def __init__(self, images: List[Any]):
        super().__init__(self.__class__.__name__)
        self.images = images
        self.occurred_at = datetime.now()