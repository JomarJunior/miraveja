from typing import ClassVar
from MiravejaCore.Shared.Events.Domain.Interfaces import DomainEvent
from MiravejaCore.Shared.Events.Domain.Services import eventRegistry
from MiravejaCore.Shared.Identifiers.Models import MemberId
from pydantic import Field


@eventRegistry.RegisterEvent(eventType="MemberConnectedEvent", eventVersion=1)
class MemberConnectedEvent(DomainEvent):
    """Event representing a member connecting via WebSocket."""

    type: ClassVar[str] = "event.member.connected"
    aggregateType: str = "Connection"
    version: ClassVar[int] = 1
    memberId: MemberId = Field(..., description="The ID of the connected member")
    connectedAt: str = Field(..., description="The timestamp when the member connected")

    @classmethod
    def Create(cls, memberId: MemberId, connectedAt: str) -> "MemberConnectedEvent":
        """
        Create a MemberConnectedEvent.

        Args:
            memberId (MemberId): The ID of the connected member.
            connectedAt (str): The timestamp when the member connected.

        Returns:
            MemberConnectedEvent: The created event.
        """
        return cls(
            aggregateId=str(memberId),
            memberId=memberId,
            connectedAt=connectedAt,
        )
