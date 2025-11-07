from MiravejaCore.Member.Application.ListAllMembers import ListAllMembersHandler
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Member.Infrastructure.MemberDependencies import MemberDependencies as MemberDependenciesBase

from MiravejaWorker.Member.Subscribers.FetchMembers import FetchMembersSubscriber


class MemberDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        MemberDependenciesBase.RegisterDependencies(container)
        container.RegisterFactories(
            {
                FetchMembersSubscriber.__name__: lambda container: FetchMembersSubscriber(
                    logger=container.Get(ILogger.__name__),
                    listAllMembersHandler=container.Get(ListAllMembersHandler.__name__),
                ),
            }
        )
