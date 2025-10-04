import re
from uuid import uuid4
from pydantic import BaseModel, Field, model_serializer, field_validator

from Miraveja.Shared.Identifiers.Exceptions import InvalidUUIDException

UUID_PATTERN = r"^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$"


class StrId(BaseModel):
    """
    Base model for string identifiers with a fixed length of 36 characters.
    """

    id: str = Field(...)

    def __str__(self) -> str:
        return self.id

    @model_serializer
    def SerializeId(self) -> str:
        return self.id

    @field_validator("id")
    @classmethod
    def ValidateId(cls, value: str) -> str:
        if not re.match(UUID_PATTERN, value, re.IGNORECASE):
            raise InvalidUUIDException(value)
        return value

    @classmethod
    def Generate(cls):
        """
        Generates a new MemberId with a unique UUID4 string.

        Returns:
            A new MemberId instance with a unique ID.
        """
        return cls(id=str(uuid4()))


class IntegerId(BaseModel):
    """
    Base model for integer identifiers.
    """

    id: int = Field(..., gt=0)


class MemberId(StrId):
    """
    Model for member identifiers, inheriting from StrId.
    """
