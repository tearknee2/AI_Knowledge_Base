# main.py
import logging
import jwt

from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Request
    )
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import (
    AppException,
    AuthenticationError,
)
from app.core.security import create_access_token,decode_access_token

from app.models.user import User

from app.schemas.document import (
    DocumentResponse,
    DocumentListItem
)
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeListItem
)
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    TokenResponse
)
from app.schemas.chat import ChatRequest, ChatResponse

from app.repositories.user_repository import UserRepository
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository

from app.services.document_processing_service import DocumentProcessingService
from app.services.document_service import DocumentService
from app.services.knowledge_base_service import KnowledgeBaseService
from app.services.user_service import UserService
from app.services.rag_service import answer_question
from app.services.conversation_service import ConversationService
from app.services.llm_service import LLMServiceError


logger = logging.getLogger(__name__)

app = FastAPI()

@app.exception_handler(AppException)
def app_exception_handler(
    request: Request,
    exc: AppException
):
    headers = {}

    if isinstance(exc, AuthenticationError):
        headers["WWW-Authenticate"] = "Bearer"

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message
        },
        headers=headers
    )

@app.exception_handler(HTTPException)
def http_exception_handler(
        request: Request,
        exc: HTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": "HTTP_ERROR",
            "message": exc.detail
        },
        headers=exc.headers
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "code":"VALIDATION_ERROR",
            "message":"请求参数校验失败",
            "details":exc.errors()
        }
    )

@app.exception_handler(Exception)
def exception_handler(
    request: Request,
    exc: Exception
    ):
        logger.error(
            "未处理的服务器内部异常",
            exc_info=(type(exc), exc, exc.__traceback__)
        )

        return JSONResponse(
            status_code=500,
            content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部出现问题"
            }
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        decoded_token = decode_access_token(token)

        user_id = decoded_token.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    user = db.query(User).filter(
        User.id == user_id
    ).one_or_none()

    if user is None:
        raise credentials_exception

    return user


@app.get("/users/me",response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = KnowledgeBaseRepository(db)
    service = KnowledgeBaseService(repository)

    knowledge_base_data = data.model_dump() # 将Pydantic模型转变为字典
    knowledge_base_data["user_id"] = current_user.id

    return service.create_knowledge_base(knowledge_base_data)


@app.get(
    "/knowledge-bases",
    response_model=list[KnowledgeListItem],
    status_code=200
)
def list_knowledge_bases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = KnowledgeBaseRepository(db)
    service = KnowledgeBaseService(repository)

    return service.get_knowledge_bases_by_user(
        user_id=current_user.id
    )


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = KnowledgeBaseRepository(db)
    service = KnowledgeBaseService(repository)

    return service.get_knowledge_base_by_id(
        knowledge_base_id,
        user_id=current_user.id
    )


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

    return service.create(user_data.model_dump())


@app.post(
    "/login",
    response_model=TokenResponse,
    status_code=200,
    responses={
        401:{
            "description":"用户名或密码错误"
        }
    }
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 1. 创建 Repository 和 Service
    repository = UserRepository(db)
    service = UserService(repository)

    # 2.验证用户名和密码
    user = service.authenticate(
        username=form_data.username,
        password=form_data.password
    )

    # 3.创建 JWT Token
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    # 4.返回 Token
    return TokenResponse(access_token=access_token)


@app.post(
    "/knowledge-bases/{knowledge_base_id}/documents",
    response_model=DocumentResponse,
    status_code=201,
)
def upload_document(
        knowledge_base_id: int,
        db: Session = Depends(get_db),
        file : UploadFile = File(...),
        current_user: User = Depends(get_current_user)
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

    return document_service.upload_document(
        knowledge_base_id,
        file,
        user_id=current_user.id
    )


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
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

    return document_service.list_documents(
        knowledge_base_id,
        user_id=current_user.id,
    )


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1.检查知识库是否存在，以及当前用户是否有权访问
    repository = KnowledgeBaseRepository(db)
    service = KnowledgeBaseService(repository)

    conversation_repository = ConversationRepository(db)
    conversation_service = ConversationService(
        conversation_repository,
        knowledge_base_service=service,
    )

    message_repository = MessageRepository(db)

    document_repository = DocumentRepository(db)

    conversation = conversation_service.get_or_create_conversation(
        knowledge_base_id=knowledge_base_id,
        title=request.question,
        conversation_id=request.conversation_id,
        user_id=current_user.id
    )

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
    except LLMServiceError:
        logger.exception("知识库聊天的大模型调用失败")
        raise

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
