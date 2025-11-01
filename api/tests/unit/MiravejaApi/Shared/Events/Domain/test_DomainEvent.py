import pytest
from datetime import datetime, timezone
from unittest.mock import patch
from pydantic import ValidationError

from MiravejaApi.Shared.Events.Domain.Interfaces import DomainEvent
from MiravejaApi.Shared.Identifiers.Models import EventId


class ConcreteDomainEventForTesting(DomainEvent):
    """Concrete implementation of DomainEvent for testing purposes."""

    testField: str = "test_value"


class TestDomainEvent:
    """Test cases for DomainEvent abstract base class."""

    def test_InitializeWithAllRequiredFields_ShouldSetCorrectValues(self):
        """Test that DomainEvent initializes with all required fields."""
        # Arrange
        testEventId = EventId.Generate()
        testType = "user.registered"
        testAggregateId = "user-123"
        testAggregateType = "User"
        testVersion = 1
        testOccurredAt = datetime.now(timezone.utc)

        # Act
        event = ConcreteDomainEventForTesting(
            id=testEventId,
            type=testType,
            aggregateId=testAggregateId,
            aggregateType=testAggregateType,
            version=testVersion,
            occurredAt=testOccurredAt,
            testField="custom_value",
        )

        # Assert
        assert event.id == testEventId
        assert event.type == testType
        assert event.aggregateId == testAggregateId
        assert event.aggregateType == testAggregateType
        assert event.version == testVersion
        assert event.occurredAt == testOccurredAt
        assert event.testField == "custom_value"

    def test_InitializeWithDefaultValues_ShouldGenerateIdAndTimestamp(self):
        """Test that DomainEvent generates default ID and timestamp when not provided."""
        # Act
        event = ConcreteDomainEventForTesting(
            type="test.event", aggregateId="agg-123", aggregateType="TestAggregate", version=1
        )

        # Assert
        assert isinstance(event.id, EventId)
        assert event.id.id is not None
        assert isinstance(event.occurredAt, datetime)
        assert event.occurredAt.tzinfo == timezone.utc

    def test_InitializeWithMissingType_ShouldRaiseValidationError(self):
        """Test that DomainEvent raises validation error when type is missing."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteDomainEventForTesting(
                aggregateId="agg-123", aggregateType="TestAggregate", version=1
            )  # type: ignore

        assert "type" in str(exc_info.value)

    def test_InitializeWithMissingAggregateId_ShouldRaiseValidationError(self):
        """Test that DomainEvent raises validation error when aggregateId is missing."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteDomainEventForTesting(type="test.event", aggregateType="TestAggregate", version=1)  # type: ignore

        assert "aggregateId" in str(exc_info.value)

    def test_InitializeWithMissingAggregateType_ShouldRaiseValidationError(self):
        """Test that DomainEvent raises validation error when aggregateType is missing."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteDomainEventForTesting(type="test.event", aggregateId="agg-123", version=1)  # type: ignore

        assert "aggregateType" in str(exc_info.value)

    def test_InitializeWithMissingVersion_ShouldRaiseValidationError(self):
        """Test that DomainEvent raises validation error when version is missing."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteDomainEventForTesting(
                type="test.event", aggregateId="agg-123", aggregateType="TestAggregate"
            )  # type: ignore

        assert "version" in str(exc_info.value)

    def test_InitializeWithZeroVersion_ShouldRaiseValidationError(self):
        """Test that DomainEvent raises validation error when version is zero."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteDomainEventForTesting(
                type="test.event", aggregateId="agg-123", aggregateType="TestAggregate", version=0
            )

        assert "version" in str(exc_info.value)

    def test_InitializeWithNegativeVersion_ShouldRaiseValidationError(self):
        """Test that DomainEvent raises validation error when version is negative."""
        with pytest.raises(ValidationError) as exc_info:
            ConcreteDomainEventForTesting(
                type="test.event", aggregateId="agg-123", aggregateType="TestAggregate", version=-1
            )

        assert "version" in str(exc_info.value)

    def test_ToKafkaMessageWithCompleteEvent_ShouldReturnCorrectMessageFormat(self):
        """Test that ToKafkaMessage returns correct Kafka message format."""
        # Arrange
        testEventId = EventId.Generate()
        testType = "order.created"
        testAggregateId = "order-456"
        testAggregateType = "Order"
        testVersion = 2
        testOccurredAt = datetime(2023, 12, 25, 10, 30, 45, tzinfo=timezone.utc)

        event = ConcreteDomainEventForTesting(
            id=testEventId,
            type=testType,
            aggregateId=testAggregateId,
            aggregateType=testAggregateType,
            version=testVersion,
            occurredAt=testOccurredAt,
            testField="kafka_test_value",
        )

        # Act
        kafkaMessage = event.ToKafkaMessage()

        # Assert
        assert kafkaMessage["eventId"] == str(testEventId)
        assert kafkaMessage["eventType"] == testType
        assert kafkaMessage["aggregateId"] == testAggregateId
        assert kafkaMessage["aggregateType"] == testAggregateType
        assert kafkaMessage["version"] == testVersion
        assert kafkaMessage["occurredAt"] == testOccurredAt.isoformat()
        assert "payload" in kafkaMessage
        assert kafkaMessage["payload"]["testField"] == "kafka_test_value"

    def test_ToKafkaMessagePayload_ShouldExcludeBaseEventFields(self):
        """Test that ToKafkaMessage payload excludes base event fields."""
        # Arrange
        event = ConcreteDomainEventForTesting(
            type="payload.test",
            aggregateId="payload-123",
            aggregateType="PayloadTest",
            version=1,
            testField="payload_specific_data",
        )

        # Act
        kafkaMessage = event.ToKafkaMessage()

        # Assert
        payload = kafkaMessage["payload"]

        # Verify base fields are excluded from payload
        assert "id" not in payload
        assert "type" not in payload
        assert "aggregateId" not in payload
        assert "aggregateType" not in payload
        assert "version" not in payload
        assert "occurredAt" not in payload

        # Verify custom fields are included in payload
        assert "testField" in payload
        assert payload["testField"] == "payload_specific_data"

    @patch("Miraveja.Shared.Identifiers.Models.uuid.uuid4")
    def test_InitializeWithMockedIdGeneration_ShouldUseGeneratedId(self, mock_uuid4):
        """Test that DomainEvent uses generated EventId when not provided."""
        # Arrange
        expected_uuid = "123e4567-e89b-12d3-a456-426614174000"
        mock_uuid4.return_value = type("MockUUID", (), {"__str__": lambda self: expected_uuid})()

        # Act
        event = ConcreteDomainEventForTesting(
            type="id.generation.test", aggregateId="id-test-123", aggregateType="IdTest", version=1
        )

        # Assert
        assert str(event.id) == expected_uuid

    def test_InitializeWithCustomOccurredAt_ShouldUseProvidedTimestamp(self):
        """Test that DomainEvent uses provided occurredAt timestamp."""
        # Arrange
        customTimestamp = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)

        # Act
        event = ConcreteDomainEventForTesting(
            type="custom.timestamp",
            aggregateId="timestamp-123",
            aggregateType="TimestampTest",
            version=1,
            occurredAt=customTimestamp,
        )

        # Assert
        assert event.occurredAt == customTimestamp

    def test_ToKafkaMessageWithEmptyPayload_ShouldReturnEmptyPayloadDict(self):
        """Test that ToKafkaMessage returns empty payload when no additional fields."""

        # Create a minimal event implementation with no extra fields
        class MinimalTestEvent(DomainEvent):
            def __init__(self, **kwargs):
                if "type" not in kwargs:
                    kwargs["type"] = "minimal.event"
                if "aggregateId" not in kwargs:
                    kwargs["aggregateId"] = "minimal-123"
                if "aggregateType" not in kwargs:
                    kwargs["aggregateType"] = "Minimal"
                if "version" not in kwargs:
                    kwargs["version"] = 1
                super().__init__(**kwargs)

        # Arrange
        event = MinimalTestEvent()

        # Act
        kafkaMessage = event.ToKafkaMessage()

        # Assert
        assert kafkaMessage["payload"] == {}
        assert len(kafkaMessage["payload"]) == 0
