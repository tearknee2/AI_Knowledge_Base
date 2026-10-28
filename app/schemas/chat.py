from pydantic import BaseModel, ConfigDict, Field

class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1)
    conversation_id: int | None = None

class ChatSource(BaseModel):
    content: str
    file_name: str | None = None
    document_id: int | None = None
    chunk_index: int | None = None
    distance:float | None = None

class ChatResponse(BaseModel):
    conversation_id: int | None = None
    question: str
    answer: str
    sources: list[ChatSource] = Field(default_factory=list)