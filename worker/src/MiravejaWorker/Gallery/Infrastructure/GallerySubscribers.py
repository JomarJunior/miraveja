from MiravejaCore.Gallery.Domain.Events import ImageMetadataRegisteredEvent
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Domain.Interfaces import IEventConsumer

from MiravejaWorker.Gallery.Subscribers.WhenImageMetadataRegistered.GenerateImageThumbnail import GenerateImageThumbnail


class GallerySubscribers:
    @staticmethod
    def RegisterSubscribers(
        eventConsumer: IEventConsumer,
        container: Container,
    ):
        eventConsumer.Subscribe(
            ImageMetadataRegisteredEvent,
            container.Get(GenerateImageThumbnail.__name__),
        )
