from MiravejaCore.Shared.Errors.Models import DomainException


class MissingEventTypeError(DomainException):
    """Raised when an event is missing the 'eventType' field."""

    def __init__(self):
        super().__init__("Event data missing 'eventType' field.")


class MissingEventVersionError(DomainException):
    """Raised when an event is missing the 'eventVersion' field."""

    def __init__(self):
        super().__init__("Event data missing 'eventVersion' field.")


class SchemaValidationError(DomainException):
    """Raised when event data does not conform to the expected schema."""

    def __init__(self, message: str):
        super().__init__(f"Schema validation error: {message}")


class EventAlreadyRegisteredError(DomainException):
    """Raised when attempting to register an event type that is already registered."""

    def __init__(self, eventType: str, eventVersion: int):
        super().__init__(f"Event type '{eventType}' with version '{eventVersion}' is already registered.")


class EventNotFoundError(DomainException):
    """Raised when an event type is not found in the registry."""

    def __init__(self, eventType: str, eventVersion: int):
        super().__init__(f"Event type '{eventType}' with version '{eventVersion}' not found in the registry.")


class SchemasDirectoryNotFoundError(DomainException):
    """Raised when the schemas directory does not exist."""

    def __init__(self, path: str):
        super().__init__(f"Schemas directory not found at path: {path}")


class SchemaFileNotFoundError(DomainException):
    """Raised when a specific schema file is not found."""

    def __init__(self, filePath: str):
        super().__init__(f"Schema file not found at path: {filePath}")


class InvalidSchemaJSONError(DomainException):
    """Raised when a schema file contains invalid JSON."""

    def __init__(self, filePath: str, errorMessage: str):
        super().__init__(f"Invalid JSON in schema file at path: {filePath}. Error: {errorMessage}")
