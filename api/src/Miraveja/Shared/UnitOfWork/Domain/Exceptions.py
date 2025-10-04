from Miraveja.Shared.Errors.Models import DomainException


class SessionNotInitializedError(DomainException):
    def __init__(self) -> None:
        super().__init__("Session is not initialized. Ensure you are within a 'with' context.")
