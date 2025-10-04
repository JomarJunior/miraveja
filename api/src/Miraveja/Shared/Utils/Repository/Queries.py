from pydantic import BaseModel, Field
from Miraveja.Shared.Utils.Repository.Enums import SortOrder


class ListAllQuery(BaseModel):
    sortBy: str = Field(default="id", min_length=1, max_length=50)
    sortOrder: SortOrder = Field(default=SortOrder.ASC)
    limit: int = Field(default=100, gt=0, le=200)
    offset: int = Field(default=0, ge=0)
