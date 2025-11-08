from MiravejaCore.Member.Application.FindMemberById import FindMemberByIdHandler
from MiravejaCore.Member.Application.ListAllMembers import ListAllMembersHandler
from MiravejaCore.Member.Application.RegisterMember import RegisterMemberHandler
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Member.Infrastructure.Sql.Repositories import SqlMemberRepository
from MiravejaCore.Shared.DatabaseManager.Infrastructure.Factories import SqlDatabaseManagerFactory
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Events.Application.EventDispatcher import EventDispatcher
from MiravejaCore.Shared.Logging.Interfaces import ILogger


class MemberDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        container.RegisterFactories(
            {
                # Repositories
                IMemberRepository.__name__: lambda container: SqlMemberRepository,
                # Handlers
                ListAllMembersHandler.__name__: lambda container: ListAllMembersHandler(
                    databaseManagerFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tMemberRepository=container.Get(IMemberRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                ),
                FindMemberByIdHandler.__name__: lambda container: FindMemberByIdHandler(
                    databaseManagerFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tMemberRepository=container.Get(IMemberRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                RegisterMemberHandler.__name__: lambda container: RegisterMemberHandler(
                    databaseManagerFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tMemberRepository=container.Get(IMemberRepository.__name__),
                    eventDispatcher=container.Get(EventDispatcher.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
