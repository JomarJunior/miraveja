"""
Models for Core Task context
"""

from src.Core.Tasks.Enums import TaskStatusEnum
from src.Core.Logging.Logger import Logger
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
from datetime import datetime
import uuid
import threading

@dataclass
class TaskResult:
    """
    Represents the result of a task.
    """
    task_id: str
    status: TaskStatusEnum
    result: Any = None
    error: Optional[Exception] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the TaskResult instance to a dictionary.
        """
        return {
            "task_id": self.task_id,
            "status": self.status,
            "result": self.result,
            "error": self.error.__str__() if self.error else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

class TaskManager:
    def __init__(self, logger: Logger):
        self.logger = logger
        self.tasks: Dict[str, TaskResult] = {}
    
    def execute(self, func: Callable, *args, detached: bool = False, **kwargs) -> TaskResult:
        task_id = str(uuid.uuid4())
        task_result = TaskResult(
            task_id=task_id,
            status=TaskStatusEnum.PENDING,
        )
        self.tasks[task_id] = task_result
        self.logger.info(f"Task {task_id} created with status {task_result.status}.")

        if detached:
            self.logger.info(f"Executing task {task_id} in detached mode.")
            # Execute asynchronously
            thread = threading.Thread(
                target=self._execute_task,
                args=(task_id, func, args, kwargs)
            )
            thread.daemon = True
            thread.start()
        else:
            self.logger.info(f"Executing task {task_id} in synchronous mode.")
            # Execute synchronously
            self._execute_task(task_id, func, args, kwargs)
        
        return self.tasks[task_id]
    
    def _execute_task(self, task_id: str, func: Callable, args: tuple, kwargs: dict) -> None:
        self.logger.info(f"Executing task {task_id}...")
        task_result = self.tasks[task_id]
        task_result.status = TaskStatusEnum.RUNNING
        task_result.started_at = datetime.now()

        try:
            result = func(*args, **kwargs)
            task_result.result = result
            task_result.status = TaskStatusEnum.COMPLETED
            self.logger.info(f"Task {task_id} completed successfully.")
        except Exception as error:
            self.logger.error(f"Error executing task {task_id}: {error}")
            task_result.error = error
            task_result.status = TaskStatusEnum.FAILED
        finally:
            task_result.completed_at = datetime.now()
            self.logger.info(f"Task {task_id} finished with status: {task_result.status}")

    def get_task_status(self, task_id: str) -> Optional[TaskResult]:
        """
        Retrieves the status of a task by its ID.
        """
        return self.tasks.get(task_id)

