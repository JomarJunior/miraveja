from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Member.Infrastructure.MemberDependencies import MemberDependencies as CoreMemberDependencies
from MiravejaCore.Shared.Logging.Interfaces import ILogger
from MiravejaCore.Member.Application.FindMemberById import FindMemberByIdHandler
from MiravejaCore.Member.Application.ListAllMembers import ListAllMembersHandler
from MiravejaCore.Member.Application.RegisterMember import RegisterMemberHandler
from MiravejaApi.Member.Infrastructure.Http.MemberController import MemberController


class MemberDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        CoreMemberDependencies.RegisterDependencies(container)
        container.RegisterFactories(
            {
                # Controllers
                MemberController.__name__: lambda container: MemberController(
                    listAllMembersHandler=container.Get(ListAllMembersHandler.__name__),
                    findMemberByIdHandler=container.Get(FindMemberByIdHandler.__name__),
                    registerMemberHandler=container.Get(RegisterMemberHandler.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
