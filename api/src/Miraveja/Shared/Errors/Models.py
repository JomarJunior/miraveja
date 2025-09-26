from typing import Any, Dict, Optional


class DomainException(Exception):
    """Base class for domain-specific exceptions."""

    def __init__(self, message: str, code: int = 400, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details
