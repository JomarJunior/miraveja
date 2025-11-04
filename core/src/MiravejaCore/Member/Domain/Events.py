from datetime import datetime, timezone
from typing import Any, ClassVar, Dict

from MiravejaCore.Shared.Events.Domain.Models import DomainEvent
from MiravejaCore.Shared.Identifiers.Models import MemberId


class MemberRegisteredEvent(DomainEvent):
    """Event representing the registration of a new member."""

    type: ClassVar[str] = "member.registered"
    aggregateType: str = "Member"
    version: int = 1
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


class MemberActivatedEvent(DomainEvent):
    """Event representing the activation of a member."""

    type: ClassVar[str] = "member.activated"
    aggregateType: str = "Member"
    version: int = 1
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


class MemberDeactivatedEvent(DomainEvent):
    """Event representing the deactivation of a member."""

    type: ClassVar[str] = "member.deactivated"
    aggregateType: str = "Member"
    version: int = 1
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


class MemberProfileUpdatedEvent(DomainEvent):
    """Event representing the update of a member's profile."""

    type: ClassVar[str] = "member.profile.updated"
    aggregateType: str = "Member"
    version: int = 1
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


class MemberIdentityUpdatedEvent(DomainEvent):
    """Event representing the update of a member's identity."""

    type: ClassVar[str] = "member.identity.updated"
    aggregateType: str = "Member"
    version: int = 1
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


class MemberAddedFriendEvent(DomainEvent):
    """Event representing a member adding a friend."""

    type: ClassVar[str] = "member.friend.added"
    aggregateType: str = "Member"
    version: int = 1
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


class MemberRemovedFriendEvent(DomainEvent):
    """Event representing a member removing a friend."""

    type: ClassVar[str] = "member.friend.removed"
    aggregateType: str = "Member"
    version: int = 1
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


class MemberFollowedEvent(DomainEvent):
    """Event representing a member following another member."""

    type: ClassVar[str] = "member.followed"
    aggregateType: str = "Member"
    version: int = 1
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


class MemberUnfollowedEvent(DomainEvent):
    """Event representing a member unfollowing another member."""

    type: ClassVar[str] = "member.unfollowed"
    aggregateType: str = "Member"
    version: int = 1
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
