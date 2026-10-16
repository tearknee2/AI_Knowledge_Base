from pydantic import BaseModel, ConfigDict, Field

class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    conversation_id: int | None = None

class ChatResponse(BaseModel):
    conversation_id: int
    question: str
    answer: str