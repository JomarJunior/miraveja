from MiravejaCore.Shared.Errors.Models import DomainException


class LoggerAlreadyExistsException(DomainException):
    """Exception raised when attempting to create a logger that already exists."""

    def __init__(self, name: str):
        super().__init__(message=f"Logger with name '{name}' already exists.", code=500)
