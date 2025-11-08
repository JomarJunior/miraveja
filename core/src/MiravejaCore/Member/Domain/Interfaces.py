from abc import ABC, abstractmethod
from typing import Iterator, Optional

from MiravejaCore.Member.Domain.Models import Member
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Utils.Repository.Queries import ListAllQuery
from MiravejaCore.Shared.Utils.Repository.Types import FilterFunction


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
