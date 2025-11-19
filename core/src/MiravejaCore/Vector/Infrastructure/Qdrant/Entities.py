from typing import Any, Dict, List, Union

from pydantic import BaseModel, Field, field_validator, model_serializer
from qdrant_client.http.models import ScoredPoint
from qdrant_client.models import PointStruct, Record
from torch import Tensor

from MiravejaCore.Shared.Errors.Models import InfrastructureException
from MiravejaCore.Vector.Domain.Models import Vector


class QdrantPoint(BaseModel):
    id: str = Field(..., description="The unique identifier of the point in Qdrant.")
    vector: List[float] = Field(..., description="The vector representation of the point.")
    payload: Dict[str, Any] = Field(..., description="Additional metadata associated with the point.")

    @field_validator("payload", mode="before")
    @classmethod
    def EnsurePayloadContainsAllNecessaryFields(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        requiredFields = Vector.model_fields.keys()
        for field in requiredFields:
            if field == "embedding":
                continue  # Embedding is stored separately, no need to check in payload
            if field == "id":
                continue  # ID is stored separately, no need to check in payload
            if field == "events":
                continue  # Events are not stored in Qdrant payload
            if field not in v:
                raise InfrastructureException(f"Payload is missing required field: {field}")

        return v

    @classmethod
    def FromDomain(cls, vector: Vector) -> "QdrantPoint":
        return QdrantPoint(
            id=str(vector.id),
            vector=vector.GetEmbeddingAsList(),
            payload=vector.model_dump(exclude={"embedding", "id"}),
        )

    @classmethod
    def FromQdrantResponse(cls, response: Union[Record, ScoredPoint]) -> "QdrantPoint":
        return QdrantPoint(
            id=str(response.id),
            vector=response.vector or [],  # type: ignore
            payload=response.payload or {},
        )

    @model_serializer
    def ToDomainDict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            **self.payload,
            "embedding": Tensor(self.vector),
        }

    def ToPointStruct(self) -> PointStruct:
        return PointStruct(
            id=self.id,
            vector=self.vector,
            payload=self.payload,
        )
