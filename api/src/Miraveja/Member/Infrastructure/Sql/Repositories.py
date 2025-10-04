from typing import Optional, Iterator

from sqlalchemy.orm import Session as DatabaseSession

from Miraveja.Member.Domain.Interfaces import IMemberRepository
from Miraveja.Member.Domain.Models import Member
from Miraveja.Member.Infrastructure.Sql.Entities import MemberEntity
from Miraveja.Shared.Identifiers.Models import MemberId
from Miraveja.Shared.Utils.Repository.Queries import ListAllQuery
from Miraveja.Shared.Utils.Repository.Types import FilterFunction


class SqlMemberRepository(IMemberRepository):
    def __init__(
        self,
        dbSession: DatabaseSession,
    ) -> None:
        self._dbSession = dbSession

    def ListAll(
        self, query: ListAllQuery = ListAllQuery(), filterFunction: Optional[FilterFunction] = None
    ) -> Iterator[Member]:
        dbQuery = self._dbSession.query(MemberEntity)

        # Apply sorting
        sortColumn = getattr(MemberEntity, query.sortBy, None)
        if sortColumn is not None:
            if query.sortOrder == query.sortOrder.ASC:
                dbQuery = dbQuery.order_by(sortColumn.asc())
            else:
                dbQuery = dbQuery.order_by(sortColumn.desc())

        # Apply pagination
        dbQuery = dbQuery.offset(query.offset).limit(query.limit)

        # Yield results as an iterator
        for entity in dbQuery.yield_per(100):  # SQLAlchemy will load 100 rows at a time
            member: Member = Member.FromDatabase(**entity.ToDict())
            # Apply in-memory filtering if a filter function is provided
            if filterFunction is not None and not filterFunction(member):
                continue
            yield member

    def Count(self) -> int:
        dbQuery = self._dbSession.query(MemberEntity)
        return dbQuery.count()

    def FindById(self, memberId: MemberId) -> Optional[Member]:
        entity = self._dbSession.get(MemberEntity, str(memberId))
        if entity is None:
            return None
        return Member.FromDatabase(**entity.ToDict())

    def MemberExists(self, memberId: MemberId) -> bool:
        entity = self._dbSession.get(MemberEntity, str(memberId))
        return entity is not None

    def Save(self, member: Member) -> None:
        entity = MemberEntity(**member.model_dump())
        try:
            self._dbSession.merge(entity)  # Insert or Update entity
            self._dbSession.commit()
        except Exception as error:
            self._dbSession.rollback()
            raise error
