"""
Unit tests for Events Domain Events.

Tests MemberConnectedEvent and other domain events.
"""

from datetime import datetime, timezone

from MiravejaCore.Shared.Events.Domain.Events import MemberConnectedEvent
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent
from MiravejaCore.Shared.Identifiers.Models import MemberId


class TestMemberConnectedEvent:
    """Tests for MemberConnectedEvent."""

    def test_Create_WithValidData_ShouldCreateEvent(self):
        # Arrange
        memberId = MemberId(id="12345678-1234-5678-1234-567812345678")
        connectedAt = "2024-11-07T10:30:00Z"

        # Act
        event = MemberConnectedEvent.Create(memberId, connectedAt)

        # Assert
        assert event.memberId == memberId
        assert event.connectedAt == connectedAt
        assert event.aggregateId == str(memberId)
        assert event.aggregateType == "event"
        assert isinstance(event, DomainEvent)

    def test_Create_WithDifferentTimestamp_ShouldSetCorrectly(self):
        # Arrange
        memberId = MemberId(id="22345678-1234-5678-1234-567812345678")
        connectedAt = "2025-01-01T00:00:00Z"

        # Act
        event = MemberConnectedEvent.Create(memberId, connectedAt)

        # Assert
        assert event.connectedAt == "2025-01-01T00:00:00Z"
        assert event.memberId.id == "22345678-1234-5678-1234-567812345678"

    def test_TypeAndVersion_ShouldHaveCorrectClassVars(self):
        # Arrange
        memberId = MemberId(id="32345678-1234-5678-1234-567812345678")
        connectedAt = datetime.now(timezone.utc).isoformat()

        # Act
        event = MemberConnectedEvent.Create(memberId, connectedAt)

        # Assert
        assert event.type == "event.member.connected"
        assert event.version == 1
        assert MemberConnectedEvent.type == "event.member.connected"
        assert MemberConnectedEvent.version == 1

    def test_Create_WithCurrentTimestamp_ShouldCreateValidEvent(self):
        # Arrange
        memberId = MemberId(id="42345678-1234-5678-1234-567812345678")
        now = datetime.now(timezone.utc)
        connectedAt = now.isoformat()

        # Act
        event = MemberConnectedEvent.Create(memberId, connectedAt)

        # Assert
        assert event.connectedAt == connectedAt
        assert event.aggregateType == "event"

    def test_Create_MultipleEvents_ShouldBeIndependent(self):
        # Arrange
        memberId1 = MemberId(id="52345678-1234-5678-1234-567812345678")
        memberId2 = MemberId(id="62345678-1234-5678-1234-567812345678")
        time1 = "2024-11-07T10:00:00Z"
        time2 = "2024-11-07T11:00:00Z"

        # Act
        event1 = MemberConnectedEvent.Create(memberId1, time1)
        event2 = MemberConnectedEvent.Create(memberId2, time2)

        # Assert
        assert event1.memberId != event2.memberId
        assert event1.connectedAt != event2.connectedAt
        assert event1.aggregateId != event2.aggregateId

    def test_Event_ShouldInheritFromDomainEvent(self):
        # Arrange
        memberId = MemberId(id="72345678-1234-5678-1234-567812345678")
        connectedAt = "2024-11-07T12:00:00Z"

        # Act
        event = MemberConnectedEvent.Create(memberId, connectedAt)

        # Assert
        assert isinstance(event, DomainEvent)
        assert hasattr(event, "aggregateId")
        assert hasattr(event, "aggregateType")
        assert hasattr(event, "occurredAt")

    def test_Create_ShouldSetAggregateIdFromMemberId(self):
        # Arrange
        memberIdValue = "82345678-1234-5678-1234-567812345678"
        memberId = MemberId(id=memberIdValue)
        connectedAt = "2024-11-07T13:00:00Z"

        # Act
        event = MemberConnectedEvent.Create(memberId, connectedAt)

        # Assert
        assert event.aggregateId == memberIdValue
        assert event.aggregateId == str(memberId)
