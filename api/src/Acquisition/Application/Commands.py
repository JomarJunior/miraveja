"""
Application commands for image acquisition.
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class AcquireImageCommand(BaseModel):
    """
    Command to acquire a specific number of images.
    """
    amount: int = Field(..., gt=0, description="Number of images to acquire")
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    detached: bool = Field(False, description="Run the acquisition in detached mode")

    @staticmethod
    def from_dict(data: dict) -> "AcquireImageCommand":
        amount = data.get("amount")
        cursor = data.get("cursor")
        detached = data.get("detached", False)

        if amount is None or not isinstance(amount, int) or amount <= 0:
            raise ValueError("The 'amount' field must be a positive integer.")

        return AcquireImageCommand(amount=amount, cursor=cursor, detached=detached)
