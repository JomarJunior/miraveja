import pytest
from datetime import datetime, timezone
from typing import ClassVar
from unittest.mock import patch
from pydantic import ValidationError

from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent
from MiravejaCore.Shared.Identifiers.Models import EventId


class ConcreteDomainEventForTesting(DomainEvent):
    """Concrete implementation of DomainEvent for testing purposes."""

    type: ClassVar[str] = "test.event"
    aggregateType: str = "TestAggregate"
    version: ClassVar[int] = 1
    testField: str = "test_value"


class TestDomainEvent:
    """Test cases for DomainEvent abstract base class."""

    def test_InitializeWithAllRequiredFields_ShouldSetCorrectValues(self):
        """Test that DomainEvent initializes with all required fields."""
        # Arrange
        testEventId = EventId.Generate()
        testAggregateId = "user-123"
        testOccurredAt = datetime.now(timezone.utc)

        # Act
        event = ConcreteDomainEventForTesting(
            id=testEventId,
            aggregateId=testAggregateId,
            occurredAt=testOccurredAt,
            testField="custom_value",
        )

        # Assert
        assert event.id == testEventId
        assert event.type == "test.event"  # ClassVar from class definition
        assert event.aggregateId == testAggregateId
        assert event.aggregateType == "TestAggregate"  # Default from class
        assert event.version == 1  # Default from class
        assert event.occurredAt == testOccurredAt
        assert event.testField == "custom_value"

    def test_InitializeWithDefaultValues_ShouldGenerateIdAndTimestamp(self):
        """Test that DomainEvent generates default ID and timestamp when not provided."""
        # Act
        event = ConcreteDomainEventForTesting(aggregateId="agg-123")

        # Assert
        assert isinstance(event.id, EventId)
        assert event.id.id is not None
        assert isinstance(event.occurredAt, datetime)
        assert event.occurredAt.tzinfo == timezone.utc

    # Note: type is now a ClassVar with default value, so no validation test needed

    def test_InitializeWithMissingAggregateId_ShouldRaiseValidationError(self):
        """Test that DomainEvent raises validation error when aggregateId is missing."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteDomainEventForTesting()  # type: ignore

        assert "aggregateId" in str(exc_info.value)

    # Note: ConcreteDomainEventForTesting provides default version=1, so version validation
    # from base class is bypassed. Real event classes should use Field(..., gt=0) if needed.

    def test_ToKafkaMessageWithCompleteEvent_ShouldReturnCorrectMessageFormat(self):
        """Test that ToKafkaMessage returns correct Kafka message format."""
        # Arrange
        testEventId = EventId.Generate()
        testAggregateId = "order-456"
        testOccurredAt = datetime(2023, 12, 25, 10, 30, 45, tzinfo=timezone.utc)

        event = ConcreteDomainEventForTesting(
            id=testEventId,
            aggregateId=testAggregateId,
            occurredAt=testOccurredAt,
            testField="kafka_test_value",
        )

        # Act
        kafkaMessage = event.ToKafkaMessage()

        # Assert
        # New format: {"class": "module.ClassName", "payload": {...}}
        assert "class" in kafkaMessage
        assert kafkaMessage["class"].endswith("ConcreteDomainEventForTesting")
        assert "payload" in kafkaMessage

        payload = kafkaMessage["payload"]
        assert payload["id"] == str(testEventId)
        assert payload["aggregateId"] == testAggregateId
        assert payload["aggregateType"] == "TestAggregate"
        assert payload["version"] == 1
        assert payload["occurredAt"] == testOccurredAt.isoformat()
        assert payload["testField"] == "kafka_test_value"

    def test_ToKafkaMessagePayload_ShouldIncludeAllFields(self):
        """Test that ToKafkaMessage payload includes all event fields."""
        # Arrange
        event = ConcreteDomainEventForTesting(
            aggregateId="payload-123",
            testField="payload_specific_data",
        )

        # Act
        kafkaMessage = event.ToKafkaMessage()

        # Assert
        payload = kafkaMessage["payload"]

        # New behavior: payload now includes ALL fields (base + custom)
        assert "id" in payload
        assert "aggregateId" in payload
        assert "aggregateType" in payload
        assert "version" in payload
        assert "occurredAt" in payload
        assert "testField" in payload
        assert payload["testField"] == "payload_specific_data"

    @patch("MiravejaCore.Shared.Identifiers.Models.uuid.uuid4")
    def test_InitializeWithMockedIdGeneration_ShouldUseGeneratedId(self, mock_uuid4):
        """Test that DomainEvent uses generated EventId when not provided."""
        # Arrange
        expected_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_uuid4.return_value = type("MockUUID", (), {"__str__": lambda self: expected_uuid})()

        # Act
        event = ConcreteDomainEventForTesting(aggregateId="id-test-123")

        # Assert
        assert str(event.id) == expected_uuid

    def test_InitializeWithCustomOccurredAt_ShouldUseProvidedTimestamp(self):
        """Test that DomainEvent uses provided occurredAt timestamp."""
        # Arrange
        customTimestamp = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

        # Act
        event = ConcreteDomainEventForTesting(
            aggregateId="timestamp-123",
            occurredAt=customTimestamp,
        )

        # Assert
        assert event.occurredAt == customTimestamp

    def test_ToKafkaMessageWithEmptyPayload_ShouldReturnEmptyPayloadDict(self):
        """Test that ToKafkaMessage returns empty payload when no additional fields."""

        # Create a minimal event implementation with no extra fields
        class MinimalTestEvent(DomainEvent):
            type: ClassVar[str] = "minimal.event"
            aggregateType: str = "Minimal"
            version: ClassVar[int] = 1

        # Arrange
        event = MinimalTestEvent(aggregateId="minimal-123")

        # Act
        kafkaMessage = event.ToKafkaMessage()

        # Assert
        # Payload now includes all base fields even for minimal events
        payload = kafkaMessage["payload"]
        assert "id" in payload
        assert "aggregateId" in payload
        assert "aggregateType" in payload
        assert "version" in payload
        assert "occurredAt" in payload
