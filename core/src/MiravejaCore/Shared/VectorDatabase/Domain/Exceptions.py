from MiravejaCore.Shared.Errors.Models import DomainException


class ClientNotInitializedError(DomainException):
    """Raised when attempting to use a vector database client that hasn't been initialized."""

    def __init__(self):
        super().__init__(
            message="Vector database client not initialized. Use the manager within a context.",
        )
