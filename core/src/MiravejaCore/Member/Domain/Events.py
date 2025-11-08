from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List

from MiravejaCore.Shared.Events.Domain.Models import DomainEvent
from MiravejaCore.Shared.Events.Domain.Services import eventRegistry
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Shared.Utils.Repository.Queries import ListAllQuery


# Q: When this decorator runs?
# A: It runs when the class is defined, registering the event with the event registry.
#    The class is defined when the module is imported.
# Q: Multiple imports cause multiple decorator executions?
# A: No, because Python caches imported modules.
@eventRegistry.RegisterEvent(eventType="member.fetch", eventVersion=1)
class FetchMembersEvent(DomainEvent, ListAllQuery):
    """Event representing a request to fetch a member."""

    type: ClassVar[str] = "member.fetch"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1

    @classmethod
    def Create(cls) -> "FetchMembersEvent":
        """
        Create a FetchMembersEvent.

        Returns:
            FetchMembersEvent: The created event.
        """
        return cls(
            aggregateId="fetch_members",
        )


@eventRegistry.RegisterEvent(eventType="members.listed", eventVersion=1)
class MembersListedEvent(DomainEvent):
    """Event representing the listing of members."""

    type: ClassVar[str] = "members.listed"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    members: List[Dict[str, Any]] = []

    @classmethod
    def Create(cls, members: List[Dict[str, Any]]) -> "MembersListedEvent":
        """
        Create a MembersListedEvent.

        Args:
            members (List[Dict[str, Any]]): The list of members.

        Returns:
            MembersListedEvent: The created event.
        """
        return cls(
            aggregateId="members_list",
            members=members,
        )


@eventRegistry.RegisterEvent(eventType="member.found", eventVersion=1)
class MemberFoundEvent(DomainEvent):
    """Event representing the finding of a member."""

    type: ClassVar[str] = "member.found"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    memberId: str
    foundAt: str

    @classmethod
    def FromMemberId(cls, memberId: MemberId) -> "MemberFoundEvent":
        """
        Create a MemberFoundEvent from a Member ID.

        Args:
            memberId (MemberId): The ID of the found member.

        Returns:
            MemberFoundEvent: The created event.
        """
        return cls(
            memberId=str(memberId),
            foundAt=str(datetime.now(timezone.utc)),
            aggregateId=str(memberId),
        )


@eventRegistry.RegisterEvent(eventType="member.registered", eventVersion=1)
class MemberRegisteredEvent(DomainEvent):
    """Event representing the registration of a new member."""

    type: ClassVar[str] = "member.registered"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    memberId: str
    email: str
    name: str

    @classmethod
    def FromModel(cls, member) -> "MemberRegisteredEvent":
        """
        Create a MemberRegisteredEvent from a Member model.

        Args:
            member (Member): The member model.

        Returns:
            MemberRegisteredEvent: The created event.
        """
        return cls(
            aggregateId=str(member.id),
            memberId=str(member.id),
            email=member.email,
            name=member.identity.fullName,
        )


@eventRegistry.RegisterEvent(eventType="member.activated", eventVersion=1)
class MemberActivatedEvent(DomainEvent):
    """Event representing the activation of a member."""

    type: ClassVar[str] = "member.activated"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    memberId: str
    activatedAt: str

    @classmethod
    def FromModel(cls, member) -> "MemberActivatedEvent":
        """
        Create a MemberActivatedEvent from a Member model.

        Args:
            member (Member): The member model.

        Returns:
            MemberActivatedEvent: The created event.
        """
        return cls(
            memberId=str(member.id),
            activatedAt=str(datetime.now(timezone.utc)),
            aggregateId=str(member.id),
        )


@eventRegistry.RegisterEvent(eventType="member.deactivated", eventVersion=1)
class MemberDeactivatedEvent(DomainEvent):
    """Event representing the deactivation of a member."""

    type: ClassVar[str] = "member.deactivated"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    memberId: str
    deactivatedAt: str

    @classmethod
    def FromModel(cls, member) -> "MemberDeactivatedEvent":
        """
        Create a MemberDeactivatedEvent from a Member model.

        Args:
            member (Member): The member model.
        Returns:
            MemberDeactivatedEvent: The created event.
        """
        return cls(
            memberId=str(member.id),
            deactivatedAt=str(datetime.now(timezone.utc)),
            aggregateId=str(member.id),
        )


@eventRegistry.RegisterEvent(eventType="member.profile.updated", eventVersion=1)
class MemberProfileUpdatedEvent(DomainEvent):
    """Event representing the update of a member's profile."""

    type: ClassVar[str] = "member.profile.updated"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    memberId: str
    oldProfile: Dict[str, Any]
    newProfile: Dict[str, Any]

    @classmethod
    def FromModel(cls, oldMember, newMember) -> "MemberProfileUpdatedEvent":
        """
        Create a MemberProfileUpdatedEvent from old and new Member models.

        Args:
            oldMember (Member): The old member model.
            newMember (Member): The new member model.
        Returns:
            MemberProfileUpdatedEvent: The created event.
        """
        return cls(
            memberId=str(newMember.id),
            oldProfile=oldMember.profile.model_dump(),
            newProfile=newMember.profile.model_dump(),
            aggregateId=str(newMember.id),
        )


@eventRegistry.RegisterEvent(eventType="member.identity.updated", eventVersion=1)
class MemberIdentityUpdatedEvent(DomainEvent):
    """Event representing the update of a member's identity."""

    type: ClassVar[str] = "member.identity.updated"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    memberId: str
    oldIdentity: Dict[str, Any]
    newIdentity: Dict[str, Any]

    @classmethod
    def FromModel(cls, oldMember, newMember) -> "MemberIdentityUpdatedEvent":
        """
        Create a MemberIdentityUpdatedEvent from old and new Member models.

        Args:
            oldMember (Member): The old member model.
            newMember (Member): The new member model.
        Returns:
            MemberIdentityUpdatedEvent: The created event.
        """
        return cls(
            memberId=str(newMember.id),
            oldIdentity=oldMember.identity.model_dump(),
            newIdentity=newMember.identity.model_dump(),
            aggregateId=str(newMember.id),
        )


@eventRegistry.RegisterEvent(eventType="member.friend.added", eventVersion=1)
class MemberAddedFriendEvent(DomainEvent):
    """Event representing a member adding a friend."""

    type: ClassVar[str] = "member.friend.added"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    memberId: str
    friendMemberId: str

    @classmethod
    def FromMembersIds(cls, memberId: MemberId, friendMemberId: MemberId) -> "MemberAddedFriendEvent":
        """
        Create a MemberAddedFriendEvent from member IDs.

        Args:
            memberId (str): The ID of the member adding a friend.
            friendMemberId (str): The ID of the friend being added.

        Returns:
            MemberAddedFriendEvent: The created event.
        """
        return cls(
            memberId=str(memberId),
            friendMemberId=str(friendMemberId),
            aggregateId=str(memberId),
        )


@eventRegistry.RegisterEvent(eventType="member.friend.removed", eventVersion=1)
class MemberRemovedFriendEvent(DomainEvent):
    """Event representing a member removing a friend."""

    type: ClassVar[str] = "member.friend.removed"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    memberId: str
    friendMemberId: str

    @classmethod
    def FromMembersIds(cls, memberId: MemberId, friendMemberId: MemberId) -> "MemberRemovedFriendEvent":
        """
        Create a MemberRemovedFriendEvent from member IDs.

        Args:
            memberId (str): The ID of the member removing a friend.
            friendMemberId (str): The ID of the friend being removed.

        Returns:
            MemberRemovedFriendEvent: The created event.
        """
        return cls(
            memberId=str(memberId),
            friendMemberId=str(friendMemberId),
            aggregateId=str(memberId),
        )


@eventRegistry.RegisterEvent(eventType="member.followed", eventVersion=1)
class MemberFollowedEvent(DomainEvent):
    """Event representing a member following another member."""

    type: ClassVar[str] = "member.followed"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    memberId: str
    followedMemberId: str

    @classmethod
    def FromMembersIds(cls, memberId: MemberId, followedMemberId: MemberId) -> "MemberFollowedEvent":
        """
        Create a MemberFollowedEvent from member IDs.

        Args:
            memberId (str): The ID of the member who followed.
            followedMemberId (str): The ID of the member being followed.

        Returns:
            MemberFollowedEvent: The created event.
        """
        return cls(
            memberId=str(memberId),
            followedMemberId=str(followedMemberId),
            aggregateId=str(memberId),
        )


@eventRegistry.RegisterEvent(eventType="member.unfollowed", eventVersion=1)
class MemberUnfollowedEvent(DomainEvent):
    """Event representing a member unfollowing another member."""

    type: ClassVar[str] = "member.unfollowed"
    aggregateType: str = "Member"
    version: ClassVar[int] = 1
    memberId: str
    unfollowedMemberId: str

    @classmethod
    def FromMembersIds(cls, memberId: MemberId, unfollowedMemberId: MemberId) -> "MemberUnfollowedEvent":
        """
        Create a MemberUnfollowedEvent from member IDs.

        Args:
            memberId (str): The ID of the member who unfollowed.
            unfollowedMemberId (str): The ID of the member being unfollowed.

        Returns:
            MemberUnfollowedEvent: The created event.
        """
        return cls(
            memberId=str(memberId),
            unfollowedMemberId=str(unfollowedMemberId),
            aggregateId=str(memberId),
        )
