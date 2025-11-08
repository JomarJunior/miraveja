import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from MiravejaCore.Member.Domain.Events import (
    FetchMembersEvent,
    MembersListedEvent,
    MemberFoundEvent,
    MemberRegisteredEvent,
    MemberActivatedEvent,
    MemberDeactivatedEvent,
    MemberProfileUpdatedEvent,
    MemberIdentityUpdatedEvent,
    MemberAddedFriendEvent,
    MemberRemovedFriendEvent,
    MemberFollowedEvent,
    MemberUnfollowedEvent,
)
from MiravejaCore.Shared.Identifiers.Models import MemberId
from MiravejaCore.Member.Domain.Models import Member, Profile, Identity


class TestFetchMembersEvent:
    """Test cases for FetchMembersEvent."""

    def test_Create_ShouldReturnEventWithCorrectAttributes(self):
        """Test that Create returns a FetchMembersEvent with correct attributes."""
        # Act
        event = FetchMembersEvent.Create()

        # Assert
        assert isinstance(event, FetchMembersEvent)
        assert event.type == "member.fetch"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.aggregateId == "fetch_members"

    def test_InitializeDirectly_ShouldSetCorrectValues(self):
        """Test that FetchMembersEvent can be initialized directly."""
        # Act
        event = FetchMembersEvent(aggregateId="test_fetch")

        # Assert
        assert event.aggregateId == "test_fetch"
        assert event.type == "member.fetch"
        assert event.aggregateType == "Member"


class TestMembersListedEvent:
    """Test cases for MembersListedEvent."""

    def test_CreateWithEmptyList_ShouldReturnEventWithEmptyMembers(self):
        """Test that Create with empty list returns event with empty members."""
        # Act
        event = MembersListedEvent.Create(members=[])

        # Assert
        assert isinstance(event, MembersListedEvent)
        assert event.type == "members.listed"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.aggregateId == "members_list"
        assert event.members == []

    def test_CreateWithMembersList_ShouldReturnEventWithMembers(self):
        """Test that Create with members list returns event with correct data."""
        # Arrange
        members = [
            {"id": "123", "email": "test1@example.com"},
            {"id": "456", "email": "test2@example.com"},
        ]

        # Act
        event = MembersListedEvent.Create(members=members)

        # Assert
        assert event.members == members
        assert len(event.members) == 2


class TestMemberFoundEvent:
    """Test cases for MemberFoundEvent."""

    def test_FromMemberId_ShouldReturnEventWithCorrectAttributes(self):
        """Test that FromMemberId creates event with member ID."""
        # Arrange
        memberId = MemberId.Generate()

        # Act
        event = MemberFoundEvent.FromMemberId(memberId)

        # Assert
        assert isinstance(event, MemberFoundEvent)
        assert event.type == "member.found"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.memberId == str(memberId)
        assert event.aggregateId == str(memberId)
        assert isinstance(event.foundAt, str)

    def test_FromMemberId_ShouldSetFoundAtTimestamp(self):
        """Test that FromMemberId sets foundAt timestamp."""
        # Arrange
        memberId = MemberId.Generate()

        # Act
        with patch("MiravejaCore.Member.Domain.Events.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            event = MemberFoundEvent.FromMemberId(memberId)

        # Assert
        assert event.foundAt == str(mock_now)


class TestMemberRegisteredEvent:
    """Test cases for MemberRegisteredEvent."""

    def test_FromModel_ShouldReturnEventWithCorrectAttributes(self):
        """Test that FromModel creates event from member model."""
        # Arrange
        memberId = MemberId.Generate()
        member = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        # Act
        event = MemberRegisteredEvent.FromModel(member)

        # Assert
        assert isinstance(event, MemberRegisteredEvent)
        assert event.type == "member.registered"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.memberId == str(memberId)
        assert event.aggregateId == str(memberId)
        assert event.email == "test@example.com"
        assert event.name == "John Doe"


class TestMemberActivatedEvent:
    """Test cases for MemberActivatedEvent."""

    def test_FromModel_ShouldReturnEventWithCorrectAttributes(self):
        """Test that FromModel creates activation event from member model."""
        # Arrange
        memberId = MemberId.Generate()
        member = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        # Act
        event = MemberActivatedEvent.FromModel(member)

        # Assert
        assert isinstance(event, MemberActivatedEvent)
        assert event.type == "member.activated"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.memberId == str(memberId)
        assert event.aggregateId == str(memberId)
        assert isinstance(event.activatedAt, str)

    def test_FromModel_ShouldSetActivatedAtTimestamp(self):
        """Test that FromModel sets activatedAt timestamp."""
        # Arrange
        memberId = MemberId.Generate()
        member = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        # Act
        with patch("MiravejaCore.Member.Domain.Events.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            event = MemberActivatedEvent.FromModel(member)

        # Assert
        assert event.activatedAt == str(mock_now)


class TestMemberDeactivatedEvent:
    """Test cases for MemberDeactivatedEvent."""

    def test_FromModel_ShouldReturnEventWithCorrectAttributes(self):
        """Test that FromModel creates deactivation event from member model."""
        # Arrange
        memberId = MemberId.Generate()
        member = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        # Act
        event = MemberDeactivatedEvent.FromModel(member)

        # Assert
        assert isinstance(event, MemberDeactivatedEvent)
        assert event.type == "member.deactivated"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.memberId == str(memberId)
        assert event.aggregateId == str(memberId)
        assert isinstance(event.deactivatedAt, str)

    def test_FromModel_ShouldSetDeactivatedAtTimestamp(self):
        """Test that FromModel sets deactivatedAt timestamp."""
        # Arrange
        memberId = MemberId.Generate()
        member = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        # Act
        with patch("MiravejaCore.Member.Domain.Events.datetime") as mock_datetime:
            mock_now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            event = MemberDeactivatedEvent.FromModel(member)

        # Assert
        assert event.deactivatedAt == str(mock_now)


class TestMemberProfileUpdatedEvent:
    """Test cases for MemberProfileUpdatedEvent."""

    def test_FromModel_ShouldReturnEventWithCorrectAttributes(self):
        """Test that FromModel creates profile update event from old and new member models."""
        # Arrange
        memberId = MemberId.Generate()
        oldMember = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="olduser", bio="Old bio"),
            identity=Identity(firstName="John", lastName="Doe"),
        )
        newMember = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="newuser", bio="New bio"),
            identity=Identity(firstName="John", lastName="Doe"),
        )

        # Act
        event = MemberProfileUpdatedEvent.FromModel(oldMember, newMember)

        # Assert
        assert isinstance(event, MemberProfileUpdatedEvent)
        assert event.type == "member.profile.updated"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.memberId == str(memberId)
        assert event.aggregateId == str(memberId)
        assert event.oldProfile["username"] == "olduser"
        assert event.newProfile["username"] == "newuser"
        assert event.oldProfile["bio"] == "Old bio"
        assert event.newProfile["bio"] == "New bio"


class TestMemberIdentityUpdatedEvent:
    """Test cases for MemberIdentityUpdatedEvent."""

    def test_FromModel_ShouldReturnEventWithCorrectAttributes(self):
        """Test that FromModel creates identity update event from old and new member models."""
        # Arrange
        memberId = MemberId.Generate()
        oldMember = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="John", lastName="Doe"),
        )
        newMember = Member(
            id=memberId,
            email="test@example.com",
            profile=Profile(username="testuser"),
            identity=Identity(firstName="Jane", lastName="Smith"),
        )

        # Act
        event = MemberIdentityUpdatedEvent.FromModel(oldMember, newMember)

        # Assert
        assert isinstance(event, MemberIdentityUpdatedEvent)
        assert event.type == "member.identity.updated"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.memberId == str(memberId)
        assert event.aggregateId == str(memberId)
        assert event.oldIdentity["firstName"] == "John"
        assert event.oldIdentity["lastName"] == "Doe"
        assert event.newIdentity["firstName"] == "Jane"
        assert event.newIdentity["lastName"] == "Smith"


class TestMemberAddedFriendEvent:
    """Test cases for MemberAddedFriendEvent."""

    def test_FromMembersIds_ShouldReturnEventWithCorrectAttributes(self):
        """Test that FromMembersIds creates friend added event from member IDs."""
        # Arrange
        memberId = MemberId.Generate()
        friendMemberId = MemberId.Generate()

        # Act
        event = MemberAddedFriendEvent.FromMembersIds(memberId, friendMemberId)

        # Assert
        assert isinstance(event, MemberAddedFriendEvent)
        assert event.type == "member.friend.added"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.memberId == str(memberId)
        assert event.friendMemberId == str(friendMemberId)
        assert event.aggregateId == str(memberId)


class TestMemberRemovedFriendEvent:
    """Test cases for MemberRemovedFriendEvent."""

    def test_FromMembersIds_ShouldReturnEventWithCorrectAttributes(self):
        """Test that FromMembersIds creates friend removed event from member IDs."""
        # Arrange
        memberId = MemberId.Generate()
        friendMemberId = MemberId.Generate()

        # Act
        event = MemberRemovedFriendEvent.FromMembersIds(memberId, friendMemberId)

        # Assert
        assert isinstance(event, MemberRemovedFriendEvent)
        assert event.type == "member.friend.removed"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.memberId == str(memberId)
        assert event.friendMemberId == str(friendMemberId)
        assert event.aggregateId == str(memberId)


class TestMemberFollowedEvent:
    """Test cases for MemberFollowedEvent."""

    def test_FromMembersIds_ShouldReturnEventWithCorrectAttributes(self):
        """Test that FromMembersIds creates member followed event from member IDs."""
        # Arrange
        memberId = MemberId.Generate()
        followedMemberId = MemberId.Generate()

        # Act
        event = MemberFollowedEvent.FromMembersIds(memberId, followedMemberId)

        # Assert
        assert isinstance(event, MemberFollowedEvent)
        assert event.type == "member.followed"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.memberId == str(memberId)
        assert event.followedMemberId == str(followedMemberId)
        assert event.aggregateId == str(memberId)


class TestMemberUnfollowedEvent:
    """Test cases for MemberUnfollowedEvent."""

    def test_FromMembersIds_ShouldReturnEventWithCorrectAttributes(self):
        """Test that FromMembersIds creates member unfollowed event from member IDs."""
        # Arrange
        memberId = MemberId.Generate()
        unfollowedMemberId = MemberId.Generate()

        # Act
        event = MemberUnfollowedEvent.FromMembersIds(memberId, unfollowedMemberId)

        # Assert
        assert isinstance(event, MemberUnfollowedEvent)
        assert event.type == "member.unfollowed"
        assert event.aggregateType == "Member"
        assert event.version == 1
        assert event.memberId == str(memberId)
        assert event.unfollowedMemberId == str(unfollowedMemberId)
        assert event.aggregateId == str(memberId)
