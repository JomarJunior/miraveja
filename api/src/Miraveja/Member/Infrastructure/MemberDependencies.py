from MiravejaCore.Member.Application.FindMemberById import FindMemberByIdHandler
from MiravejaCore.Member.Application.ListAllMembers import ListAllMembersHandler
from MiravejaCore.Member.Application.RegisterMember import RegisterMemberHandler
from MiravejaCore.Member.Domain.Interfaces import IMemberRepository
from MiravejaCore.Shared.DatabaseManager.Infrastructure.Factories import SqlDatabaseManagerFactory
from MiravejaCore.Shared.DI.Models import Container
from MiravejaCore.Shared.Logging.Interfaces import ILogger

from Miraveja.Member.Infrastructure.Http.MemberController import MemberController
from Miraveja.Member.Infrastructure.Sql.Repositories import SqlMemberRepository


class MemberDependencies:
    @staticmethod
    def RegisterDependencies(container: Container):
        container.RegisterFactories(
            {
                # Repositories
                IMemberRepository.__name__: lambda container: SqlMemberRepository,
                # Handlers
                ListAllMembersHandler.__name__: lambda container: ListAllMembersHandler(
                    databaseUOWFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tMemberRepository=container.Get(IMemberRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                FindMemberByIdHandler.__name__: lambda container: FindMemberByIdHandler(
                    databaseUOWFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tMemberRepository=container.Get(IMemberRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                RegisterMemberHandler.__name__: lambda container: RegisterMemberHandler(
                    databaseUOWFactory=container.Get(SqlDatabaseManagerFactory.__name__),
                    tMemberRepository=container.Get(IMemberRepository.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
                # Controllers
                MemberController.__name__: lambda container: MemberController(
                    listAllMembersHandler=container.Get(ListAllMembersHandler.__name__),
                    findMemberByIdHandler=container.Get(FindMemberByIdHandler.__name__),
                    registerMemberHandler=container.Get(RegisterMemberHandler.__name__),
                    logger=container.Get(ILogger.__name__),
                ),
            }
        )
