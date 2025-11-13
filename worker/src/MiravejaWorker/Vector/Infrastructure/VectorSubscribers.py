from MiravejaCore.Gallery.Domain.Events import ImageMetadataRegisteredEvent
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Domain.Interfaces import IEventConsumer

from MiravejaWorker.Vector.Subscribers.WhenImageMetadataRegistered.GenerateImageVector import (
    GenerateImageVector,
)


class VectorSubscribers:
    @staticmethod
    def RegisterSubscribers(
        eventConsumer: IEventConsumer,
        container: Container,
    ):
        eventConsumer.Subscribe(
            ImageMetadataRegisteredEvent,
            container.Get(GenerateImageVector.__name__),
        )
