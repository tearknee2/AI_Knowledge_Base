# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.knowledge_base import(
    KnowledgeBaseCreate,
    KnowledgeBaseResponse
)
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.services.knowledge_base_service import (
    KnowledgeBaseService,
    BusinessException
)


app = FastAPI()

@app.get("/")
async def get():
    return {"hello":"world"}

@app.post(
    "/knowledge-bases",
    response_model=KnowledgeBaseResponse,
    status_code=201
)
def create_knowledge_base(
    data: KnowledgeBaseCreate,
    db: Session = Depends(get_db)
):
    repository = KnowledgeBaseRepository(db)
    service = KnowledgeBaseService(repository)

    knowledge_base_data = data.model_dump() # 将Pydantic模型转变为字典
    knowledge_base_data["user_id"] = 1 # 暂时使用测试用户id
    try:
        return service.create_knowledge_base(knowledge_base_data)
    except BusinessException as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        ) from exc
