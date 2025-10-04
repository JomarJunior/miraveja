from typing import Optional, Iterator
from abc import ABC, abstractmethod

from Miraveja.Member.Domain.Models import Member
from Miraveja.Shared.Identifiers.Models import MemberId
from Miraveja.Shared.Utils.Repository.Queries import ListAllQuery
from Miraveja.Shared.Utils.Repository.Types import FilterFunction


class IMemberRepository(ABC):
    @abstractmethod
    def ListAll(
        self, query: ListAllQuery = ListAllQuery(), filterFunction: Optional[FilterFunction] = None
    ) -> Iterator[Member]:
        pass

    @abstractmethod
    def Count(self) -> int:
        pass

    @abstractmethod
    def FindById(self, memberId: MemberId) -> Optional[Member]:
        pass

    @abstractmethod
    def MemberExists(self, memberId: MemberId) -> bool:
        pass

    @abstractmethod
    def Save(self, member: Member) -> None:
        pass
