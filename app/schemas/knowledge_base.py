# knowledge_base.py
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Literal

class KnowledgeBaseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=20)
    description: str | None = None

class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    description: str | None
    status: Literal["ACTIVE", "DISABLED"]
    created_at: datetime
    updated_at: datetime

class KnowledgeListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str = Field(min_length=1, max_length=20)
    description: str | None = None
    status: Literal["ACTIVE", "DISABLED"]
    created_at: datetime
    updated_at: datetime
