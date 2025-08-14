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
