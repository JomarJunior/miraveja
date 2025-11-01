import re
from typing import Any
import uuid
from pydantic import BaseModel, Field, model_serializer, field_validator, model_validator

from MiravejaCore.Shared.Identifiers.Exceptions import InvalidUUIDException

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

    def __eq__(self, value: object) -> bool:
        # Allow comparison with both StrId and its subclasses
        if not isinstance(value, self.__class__) and not isinstance(value, StrId):
            return False
        return self.id == value.id

    def __hash__(self) -> int:
        return hash(self.id)

    @model_validator(mode="before")
    def NormalizeFromStringOrUUID(cls, value: Any) -> object:
        if isinstance(value, (str, uuid.UUID)):
            return {"id": str(value)}
        return value

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
        return cls(id=str(uuid.uuid4()))


class IntegerId(BaseModel):
    """
    Base model for integer identifiers.
    """

    id: int = Field(..., gt=0)

    def __hash__(self) -> int:
        return hash(self.id)

    def __int__(self) -> int:
        return self.id

    @model_serializer
    def SerializeId(self) -> int:
        return self.id

    @model_validator(mode="before")
    def NormalizeFromInteger(cls, value: object) -> object:
        if isinstance(value, int):
            return {"id": value}
        return value


class MemberId(StrId):
    """
    Model for member identifiers, inheriting from StrId.
    """


class EventId(StrId):
    """
    Model for event identifiers, inheriting from StrId.
    """


class AggregateId(StrId):
    """
    Model for aggregate identifiers, inheriting from StrId.
    """


class ImageMetadataId(IntegerId):
    """
    Model for image metadata identifiers, inheriting from IntegerId.
    """


class GenerationMetadataId(IntegerId):
    """
    Model for generation metadata identifiers, inheriting from IntegerId.
    """


class LoraMetadataId(IntegerId):
    """
    Model for LoRA metadata identifiers, inheriting from IntegerId.
    """


class VectorId(IntegerId):
    """
    Model for vector identifiers, inheriting from IntegerId.
    """
