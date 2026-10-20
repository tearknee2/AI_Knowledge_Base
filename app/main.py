# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeListItem
)
from app.schemas.user import UserCreate, UserResponse
from app.repositories.user_repository import UserRepository
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.services.knowledge_base_service import (
    KnowledgeBaseService,
    BusinessException
)
from app.services.user_service import (
    UserService,
    BusinessException as UserBusinessException
)

app = FastAPI()

@app.get("/")
async def get():
    return {"hello":"world"}


@app.post(
    "/knowledge-bases",
    response_model=KnowledgeBaseResponse,
    status_code=201,
    responses={
        409:{
            "description":"知识库名称已经存在",
        },
    },
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


@app.get(
    # "/knowledgebases/{user_id}/documents",
    "/knowledge-bases",
    response_model=list[KnowledgeListItem],
    status_code=200
)
def list_knowledge_bases(
    db: Session = Depends(get_db)
):
    repository = KnowledgeBaseRepository(db)

    service = KnowledgeBaseService(repository)

    return service.get_knowledge_bases_by_user(user_id=1)

@app.get(
    "/knowledge-bases/{knowledge_base_id}",
    response_model=KnowledgeBaseResponse,
    status_code=200,
    responses={
        404:{
            "description":"知识库不存在或无权访问"
        }
    }
)
def get_knowledge_base_by_id(
    knowledge_base_id: int,
    db: Session = Depends(get_db)
):
    repository = KnowledgeBaseRepository(db)

    service = KnowledgeBaseService(repository)

    try:
        result = service.get_knowledge_base_by_id(knowledge_base_id, user_id=1)
    except BusinessException as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc
    return result


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    repository = UserRepository(db)
    service = UserService(repository)

    try:
        result = service.create(user_data.model_dump())
        # model_dump() 是 Pydantic 的方法，将模型实例转换为普通字典
    except UserBusinessException as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        ) from exc
    return result