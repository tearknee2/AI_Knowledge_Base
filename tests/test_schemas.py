# Schema 层单元测试：校验各响应/请求模型的字段集合、字段约束与非法输入拒绝。
# 由 verify/ 下 6 个脚本式校验文件重写而来（原文件为模块级 assert / try-print，无 test 函数）。
import datetime

import pytest
from pydantic import ValidationError

from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.schemas.document import (
    DocumentListItem,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.schemas.knowledge_base import (
    KnowledgeBaseCreate,
    KnowledgeBaseResponse,
    KnowledgeListItem,
)
from app.schemas.user import UserCreate, UserResponse

DOCUMENT_STATUSES = [
    "PENDING",
    "PARSING",
    "CHUNKING",
    "EMBEDDING",
    "COMPLETED",
    "FAILED",
]

NOW = datetime.datetime(2026, 11, 1, 12, 0, 0)


# ---------- DocumentResponse ----------

class FakeDocument:
    """模拟 ORM 对象：比响应 Schema 多出不应暴露的内部字段。"""

    def __init__(self):
        self.id = 1
        self.file_name = "test.txt"
        self.file_type = "txt"
        self.file_size = 100
        self.status = "PENDING"
        self.created_at = NOW
        self.file_path = "uploads/test.txt"
        self.error_message = None


def test_document_response_field_set_is_exact():
    document = DocumentResponse(
        id=1,
        file_name="test.txt",
        file_type="txt",
        file_size=100,
        status="PENDING",
        created_at=NOW,
    )
    assert set(document.model_dump()) == {
        "id", "file_name", "file_type", "file_size", "status", "created_at",
    }


def test_document_response_from_attributes_hides_internal_fields():
    response = DocumentResponse.model_validate(FakeDocument())
    assert "file_path" not in response.model_dump()
    assert "error_message" not in response.model_dump()


@pytest.mark.parametrize("status", DOCUMENT_STATUSES)
def test_document_response_accepts_all_legal_statuses(status):
    document = DocumentResponse(
        id=1, file_name="test.txt", file_type="txt",
        file_size=100, status=status, created_at=NOW,
    )
    assert document.status == status


def test_document_response_rejects_illegal_status():
    fake = FakeDocument()
    fake.status = "active"  # 不在 Literal 枚举内（大小写敏感）
    with pytest.raises(ValidationError):
        DocumentResponse.model_validate(fake)


def test_document_response_file_name_length_boundary():
    kwargs = dict(file_type="txt", file_size=1, status="PENDING", created_at=NOW)
    assert DocumentResponse(id=1, file_name="a" * 255, **kwargs).file_name
    with pytest.raises(ValidationError):
        DocumentResponse(id=1, file_name="a" * 256, **kwargs)


# ---------- DocumentUploadResponse ----------

class FakeUpload:
    def __init__(self):
        self.id = 1
        self.knowledge_base_id = 1
        self.file_name = "test.txt"
        self.status = "PENDING"
        self.created_at = NOW
        self.file_path = "uploads/test.txt"
        self.error_message = None


def test_document_upload_response_field_set_is_exact():
    response = DocumentUploadResponse(
        id=1, knowledge_base_id=11, file_name="test.txt",
        status="PENDING", created_at=NOW,
    )
    assert set(response.model_dump()) == {
        "id", "knowledge_base_id", "file_name", "status", "created_at",
    }


def test_document_upload_response_hides_internal_fields_and_rejects_bad_status():
    response = DocumentUploadResponse.model_validate(FakeUpload())
    dumped = response.model_dump()
    assert "file_path" not in dumped
    assert "error_message" not in dumped

    fake = FakeUpload()
    fake.status = "ACTIVE"  # 文档状态枚举里没有 ACTIVE
    with pytest.raises(ValidationError):
        DocumentUploadResponse.model_validate(fake)


# ---------- DocumentListItem ----------

def _document_list_item_kwargs(**overrides):
    kwargs = dict(
        id=1,
        knowledge_base_id=2,
        file_name="test.txt",
        file_type="txt",
        file_size=3,
        status="PENDING",
        error_message=None,
        created_at=NOW,
        updated_at=NOW,
    )
    kwargs.update(overrides)
    return kwargs


def test_document_list_item_field_set_is_exact():
    item = DocumentListItem(**_document_list_item_kwargs())
    assert set(item.model_dump()) == {
        "id", "knowledge_base_id", "file_name", "file_type", "file_size",
        "status", "error_message", "created_at", "updated_at",
    }
    assert "file_path" not in item.model_dump()


def test_document_list_item_error_message_accepts_text():
    item = DocumentListItem(**_document_list_item_kwargs(error_message="解析失败"))
    assert item.error_message == "解析失败"


def test_document_list_item_rejects_unknown_status():
    with pytest.raises(ValidationError):
        DocumentListItem(**_document_list_item_kwargs(status="UNKNOWN"))


# ---------- KnowledgeBaseCreate ----------

def test_knowledge_base_create_description_is_optional():
    with_description = KnowledgeBaseCreate(name="技术文档", description="存放项目技术资料")
    omitted = KnowledgeBaseCreate(name="技术文档")
    explicit_none = KnowledgeBaseCreate(name="技术文档", description=None)
    assert with_description.description == "存放项目技术资料"
    assert omitted.description is None
    assert explicit_none.description is None


@pytest.mark.parametrize("name", ["", "a" * 21, "这是一个超过二十个字符长度的知识库名称,现在才是"])
def test_knowledge_base_create_rejects_invalid_name_length(name):
    with pytest.raises(ValidationError):
        KnowledgeBaseCreate(name=name)


def test_knowledge_base_create_name_length_boundary():
    assert KnowledgeBaseCreate(name="a" * 20).name == "a" * 20


def test_knowledge_base_create_rejects_extra_fields():
    with pytest.raises(ValidationError):
        KnowledgeBaseCreate(name="技术文档", description="存放项目技术资料", status="PENDING")


# ---------- KnowledgeBaseResponse ----------

class FakeKnowledgeBase:
    def __init__(self):
        self.id = 1
        self.user_id = 10
        self.name = "技术文档"
        self.description = "存放项目技术文档"
        self.status = "ACTIVE"
        self.created_at = NOW
        self.updated_at = NOW


def test_knowledge_base_response_field_set_is_exact():
    response = KnowledgeBaseResponse.model_validate(FakeKnowledgeBase())
    assert set(response.model_dump()) == {
        "id", "user_id", "name", "description", "status", "created_at", "updated_at",
    }


def test_knowledge_base_response_allows_none_description():
    fake = FakeKnowledgeBase()
    fake.description = None
    assert KnowledgeBaseResponse.model_validate(fake).description is None


def test_knowledge_base_response_rejects_document_status():
    fake = FakeKnowledgeBase()
    fake.status = "PENDING"  # 知识库状态只有 ACTIVE / DISABLED
    with pytest.raises(ValidationError):
        KnowledgeBaseResponse.model_validate(fake)


# ---------- KnowledgeListItem ----------

class FakeListItem:
    def __init__(self):
        self.id = 1
        self.user_id = 100  # ORM 对象中的内部字段，列表项不应暴露
        self.name = "数学"
        self.description = "数学是世界上最好的学科"
        self.status = "ACTIVE"
        self.created_at = NOW
        self.updated_at = NOW


def test_knowledge_list_item_hides_user_id():
    item = KnowledgeListItem.model_validate(FakeListItem())
    assert set(item.model_dump()) == {
        "id", "name", "description", "status", "created_at", "updated_at",
    }
    assert "user_id" not in item.model_dump()


def test_knowledge_list_item_rejects_illegal_status():
    fake = FakeListItem()
    fake.status = "PENDING"
    with pytest.raises(ValidationError):
        KnowledgeListItem.model_validate(fake)


# ---------- ChatRequest / ChatResponse ----------

def test_chat_request_conversation_id_is_optional():
    assert ChatRequest(question="什么是RAG？", conversation_id=1).conversation_id == 1
    assert ChatRequest(question="什么是RAG？").conversation_id is None


def test_chat_request_rejects_empty_question():
    with pytest.raises(ValidationError):
        ChatRequest(conversation_id=12, question="")


def test_chat_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        ChatRequest(question="What is your name?", user_id=2)


def test_chat_response_sources_default_to_empty_list():
    response = ChatResponse(conversation_id=1, question="你好", answer="你好，世界")
    assert response.sources == []


def test_chat_source_optional_fields_default_to_none():
    source = ChatSource(content="相关文档片段")
    assert source.file_name is None
    assert source.document_id is None
    assert source.chunk_index is None
    assert source.distance is None


# ---------- UserCreate / UserResponse ----------

def test_user_create_valid():
    user = UserCreate(username="alice", password="password123")
    assert user.username == "alice"


@pytest.mark.parametrize("username", ["ab", "a" * 31])
def test_user_create_rejects_invalid_username_length(username):
    with pytest.raises(ValidationError):
        UserCreate(username=username, password="password123")


@pytest.mark.parametrize("username", ["abc", "a" * 30])
def test_user_create_username_length_boundary(username):
    assert UserCreate(username=username, password="password123").username == username


@pytest.mark.parametrize("password", ["1234567", "123"])
def test_user_create_rejects_short_password(password):
    with pytest.raises(ValidationError):
        UserCreate(username="alice", password=password)


def test_user_create_password_length_boundary():
    assert UserCreate(username="alice", password="a" * 8).password == "a" * 8


def test_user_create_rejects_extra_fields():
    with pytest.raises(ValidationError):
        UserCreate(username="alice", password="password123", user_id=1)


class FakeUser:
    def __init__(self):
        self.id = 2
        self.username = "alice"
        self.created_at = NOW
        self.password_hash = "fake-hash"  # 响应 Schema 不应暴露


def test_user_response_never_exposes_password_hash():
    response = UserResponse.model_validate(FakeUser())
    assert set(response.model_dump()) == {"id", "username", "created_at"}
    assert "password_hash" not in response.model_dump()
