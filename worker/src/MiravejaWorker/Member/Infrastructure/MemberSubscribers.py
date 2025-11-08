from MiravejaCore.Member.Domain.Events import FetchMembersEvent
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Domain.Interfaces import IEventConsumer
from MiravejaWorker.Member.Subscribers.FetchMembers import FetchMembersSubscriber


class MemberSubscribers:
    @staticmethod
    def RegisterSubscribers(
        eventConsumer: IEventConsumer,
        container: Container,
    ):
        eventConsumer.Subscribe(
            FetchMembersEvent,
            container.Get(FetchMembersSubscriber.__name__),
        )
