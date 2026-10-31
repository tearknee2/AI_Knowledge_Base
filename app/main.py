# main.py
import logging
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.document import (
    DocumentResponse,
    DocumentListItem
)
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeListItem
)
from app.schemas.user import UserCreate, UserResponse
from app.schemas.chat import ChatRequest, ChatResponse

from app.repositories.user_repository import UserRepository
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository

from app.services.document_processing_service import DocumentProcessingService
from app.services.document_service import DocumentService
from app.services.knowledge_base_service import (
    KnowledgeBaseService,
    BusinessException
)
from app.services.user_service import (
    UserService,
    BusinessException as UserBusinessException
)
from app.services.rag_service import answer_question
from app.services.conversation_service import ConversationService
from app.services.llm_service import LLMServiceError


logger = logging.getLogger(__name__)

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
    responses={
        409:{
            "description":"用户名重复"
        }
    }
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


@app.post(
    "/knowledge-bases/{knowledge_base_id}/documents",
    response_model=DocumentResponse,
    status_code=201,
)
def upload_document(
        knowledge_base_id: int,
        db: Session = Depends(get_db),
        file : UploadFile = File(...)
):
    knowledge_base_repository = KnowledgeBaseRepository(db)
    knowledge_base_service = KnowledgeBaseService(knowledge_base_repository)
    document_repository = DocumentRepository(db)
    document_processing_service = DocumentProcessingService(document_repository)
    document_service = DocumentService(
        document_repository,
        knowledge_base_service,
        document_processing_service
    )
    try:
        result = document_service.upload_document(knowledge_base_id, file)
        return result
    except BusinessException as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc

@app.get(
    "/knowledge-bases/{knowledge_base_id}/documents",
    response_model=list[DocumentListItem],
    status_code=200,
    responses={
        404:{
            "description": "知识库不存在或者无权访问"
        }
    }
)
def list_documents(
    knowledge_base_id: int,
    db: Session = Depends(get_db)
):
    knowledge_base_repository = KnowledgeBaseRepository(db)
    knowledge_base_service = KnowledgeBaseService(knowledge_base_repository)

    document_repository = DocumentRepository(db)
    document_processing_service = DocumentProcessingService(document_repository)

    document_service = DocumentService(
        document_repository,
        knowledge_base_service,
        document_processing_service
    )
    try:
        result = document_service.list_documents(
            knowledge_base_id,
            user_id=1,
        )
        return result
    except BusinessException as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc


@app.post(
    "/knowledge-bases/{knowledge_base_id}/chat",
    response_model=ChatResponse,
    status_code=200,
    responses={
        404:{
            "description":"知识库不存在或者无权访问"
        }
    }
)
async def chat_with_knowledge_base(
    knowledge_base_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    # 1.检查知识库是否存在，以及当前临时用户是否有权访问
    repository = KnowledgeBaseRepository(db)
    service = KnowledgeBaseService(repository)

    conversation_repository = ConversationRepository(db)
    conversation_service = ConversationService(
        conversation_repository,
        knowledge_base_service=service,
    )

    message_repository = MessageRepository(db)

    document_repository = DocumentRepository(db)
    try:
        conversation = conversation_service.get_or_create_conversation(
            knowledge_base_id=knowledge_base_id,
            title=request.question,
            conversation_id=request.conversation_id,
            user_id=1
        )
    except BusinessException as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc

    message_repository.create(
        conversation_id=conversation.id,
        role="user",
        content=request.question
    )

    n_results = 4

    # 2.执行完整的RAG回答
    try:
        result = await answer_question(
            question=request.question,
            knowledge_base_id=knowledge_base_id,
            document_repository=document_repository,
            n_results=n_results,
        )
    except LLMServiceError as exc:
        logger.exception("知识库聊天的大模型调用失败")
        raise HTTPException(
            status_code=502,
            detail="大模型服务暂时无法正常处理请求"
        ) from exc
    except Exception as exc:
        logger.exception("知识库聊天处理失败")
        raise HTTPException(
            status_code=500,
            detail="知识库问答失败"
        ) from exc

    message_repository.create(
        conversation_id=conversation.id,
        role="assistant",
        content=result["answer"],
    )

    # 3.组织符合ChatResponse的响应数据
    return ChatResponse(
        conversation_id=conversation.id,
        question=request.question,
        answer=result["answer"],
        sources=result["sources"]
    )












