"""
Enums for Task Management
"""

from enum import Enum

class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

    def __str__(self):
        return self.value