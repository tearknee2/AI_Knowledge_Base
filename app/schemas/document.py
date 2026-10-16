from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class DocumentUploadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    knowledge_base_id : int
    file_name :str = Field(max_length=255)
    status : str
    created_at : datetime

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    file_name : str = Field(max_length=255)
    file_type: str = Field(max_length=20)
    file_size: int
    status: str
    created_at : datetime