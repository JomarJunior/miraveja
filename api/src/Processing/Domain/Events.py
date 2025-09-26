"""
Events for image processing.
"""

from src.Core.Events.Base import BaseEvent
from datetime import datetime

class ImageEmbeddingCreatedEvent(BaseEvent):
    """
    Event emitted when a new image embedding is created.
    """
    def __init__(self, image_embedding):
        super().__init__(self.__class__.__name__)
        self.image_embedding = image_embedding
        self.occured_at = datetime.now()

class TextEmbeddingCreatedEvent(BaseEvent):
    """
    Event emitted when a new text embedding is created.
    """
    def __init__(self, text_embedding):
        super().__init__(self.__class__.__name__)
        self.text_embedding = text_embedding
        self.occured_at = datetime.now()

class ImageThumbnailCreatedEvent(BaseEvent):
    """
    Event emitted when a new image thumbnail is created.
    """
    def __init__(self, image_thumbnail):
        super().__init__(self.__class__.__name__)
        self.image_thumbnail = image_thumbnail
        self.occured_at = datetime.now()