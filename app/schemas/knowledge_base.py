# knowledge_base.py
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class KnowledgeBaseCreate(BaseModel):
    name: str = Field(max_length=20)
    description: str | None = None

class KnowledgeBaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime