# API 层测试：TestClient + dependency_overrides 把 get_db 换成 SQLite 内存会话，
# 验证"路由 -> 服务 -> 仓储"全链路。涉及向量库/大模型的环节用 monkeypatch 隔离，
# 因此整个套件不加载嵌入模型、不调用大模型、不写真实 ChromaDB。
from contextlib import suppress
from pathlib import Path
from unittest.mock import AsyncMock

from app.models.conversation import Conversation
from app.models.document import Document
from app.models.message import Message
from app.models.user import User
from app.services.document_processing_service import DocumentProcessingService
from app.services.llm_service import LLMServiceError


# ---------- 基础 ----------

def test_root_endpoint(api_client):
    resp = api_client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"hello": "world"}


# ---------- 用户注册 ----------

def test_create_user_success(api_client, db_session):
    resp = api_client.post(
        "/users",
        json={"username": "alice", "password": "password123"},
    )
    assert resp.status_code == 201
    body = resp.json()
    # UserResponse 只暴露 id/username/created_at，绝不返回密码或哈希
    assert set(body) == {"id", "username", "created_at"}

    row = db_session.query(User).filter_by(username="alice").one()
    # 落库的是哈希，不是明文
    assert row.password_hash != "password123"
    assert len(row.password_hash) > 20


def test_create_user_duplicate_username_conflict(api_client):
    api_client.post("/users", json={"username": "alice", "password": "password123"})
    resp = api_client.post(
        "/users",
        json={"username": "alice", "password": "password456"},
    )
    assert resp.status_code == 409


# ---------- 知识库 ----------

def test_create_knowledge_base_success(api_client, seed_user):
    resp = api_client.post(
        "/knowledge-bases",
        json={"name": "技术文档", "description": "存放项目技术资料"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "技术文档"
    assert body["status"] == "ACTIVE"  # 服务层默认置为 ACTIVE
    assert body["user_id"] == seed_user.id  # 断言知识库归属于当前测试用户（seed_user)


def test_create_knowledge_base_duplicate_name_conflict(api_client, seed_user):
    api_client.post("/knowledge-bases", json={"name": "技术文档"})
    resp = api_client.post("/knowledge-bases", json={"name": "技术文档"})
    assert resp.status_code == 409


def test_get_knowledge_base_by_id(api_client, seed_user):
    created = api_client.post(
        "/knowledge-bases", json={"name": "技术文档"}
    ).json()
    kb_id = created["id"]

    resp = api_client.get(f"/knowledge-bases/{kb_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == kb_id

    missing = api_client.get("/knowledge-bases/9999")
    assert missing.status_code == 404


def test_list_knowledge_bases_returns_created_ones(api_client, seed_user):
    api_client.post("/knowledge-bases", json={"name": "数学"})
    api_client.post("/knowledge-bases", json={"name": "物理"})

    resp = api_client.get("/knowledge-bases")
    assert resp.status_code == 200
    assert [kb["name"] for kb in resp.json()] == ["数学", "物理"]


# ---------- 文档 ----------

def test_list_documents_empty_for_new_knowledge_base(api_client, seed_user):
    kb_id = api_client.post("/knowledge-bases", json={"name": "技术文档"}).json()["id"]

    resp = api_client.get(f"/knowledge-bases/{kb_id}/documents")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_documents_missing_knowledge_base_404(api_client, seed_user):
    resp = api_client.get("/knowledge-bases/9999/documents")
    assert resp.status_code == 404


def test_upload_document_success(api_client, db_session, seed_user, monkeypatch):
    kb_id = api_client.post("/knowledge-bases", json={"name": "技术文档"}).json()["id"]

    # 向量化会加载嵌入模型并写真实 ChromaDB，测试中替换为记录调用的假函数，
    # 只验证上传链路正确触发了它
    store_calls = []

    def fake_store_document_vectors(self, document_id):
        store_calls.append(document_id)

    monkeypatch.setattr(
        DocumentProcessingService,
        "store_document_vectors",
        fake_store_document_vectors,
    )

    content = "第一行\n第二行\n"
    resp = api_client.post(
        f"/knowledge-bases/{kb_id}/documents",
        files={"file": ("hello.txt", content.encode("utf-8"), "text/plain")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["file_name"] == "hello.txt"
    assert body["file_type"] == "txt"
    assert body["file_size"] == len(content.encode("utf-8"))
    assert body["status"] == "PENDING"
    # DocumentResponse 不暴露服务器磁盘路径
    assert "file_path" not in body
    assert store_calls == [body["id"]]

    # 落库校验；随后只清理本测试写入的文件（目录非空时 rmdir 会失败，安全）
    row = db_session.query(Document).filter_by(knowledge_base_id=kb_id).one()
    save_path = Path(row.file_path)
    try:
        assert save_path.exists()
        assert save_path.read_bytes() == content.encode("utf-8")
    finally:
        save_path.unlink(missing_ok=True)
        with suppress(OSError):
            save_path.parent.rmdir()


def test_upload_document_missing_knowledge_base_404(api_client, db_session, seed_user):
    resp = api_client.post(
        "/knowledge-bases/9999/documents",
        files={"file": ("hello.txt", b"content", "text/plain")},
    )
    assert resp.status_code == 404
    assert db_session.query(Document).count() == 0


# ---------- 问答（chat） ----------

def _create_kb(api_client, name="技术文档"):
    return api_client.post("/knowledge-bases", json={"name": name}).json()["id"]


def test_chat_returns_answer_and_persists_messages(
    api_client, db_session, seed_user, monkeypatch
):
    kb_id = _create_kb(api_client)

    answer_mock = AsyncMock(
        return_value={
            "answer": "负责人是陈思远",
            "sources": [
                {"content": "项目负责人：陈思远", "file_name": "云帆.txt", "document_id": 1}
            ],
        }
    )
    monkeypatch.setattr("app.main.answer_question", answer_mock)

    resp = api_client.post(
        f"/knowledge-bases/{kb_id}/chat",
        json={"question": "云帆计划负责人是谁？"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["question"] == "云帆计划负责人是谁？"
    assert body["answer"] == "负责人是陈思远"
    assert body["sources"][0]["document_id"] == 1

    # 会话与两条消息（user + assistant）已落库
    conversation = db_session.query(Conversation).one()
    assert conversation.knowledge_base_id == kb_id
    roles = [m.role for m in db_session.query(Message).all()]
    assert roles == ["user", "assistant"]

    # 大模型收到的参数
    answer_mock.assert_awaited_once()
    assert answer_mock.await_args.kwargs["question"] == "云帆计划负责人是谁？"


def test_chat_llm_failure_returns_502_and_keeps_user_message(
    api_client, db_session, seed_user, monkeypatch
):
    kb_id = _create_kb(api_client)
    monkeypatch.setattr(
        "app.main.answer_question",
        AsyncMock(side_effect=LLMServiceError("大模型调用失败")),
    )

    resp = api_client.post(
        f"/knowledge-bases/{kb_id}/chat",
        json={"question": "云帆计划负责人是谁？"},
    )
    assert resp.status_code == 502

    # 用户消息在大模型调用前已落库，失败时不产生 assistant 回复
    messages = db_session.query(Message).all()
    assert len(messages) == 1
    assert messages[0].role == "user"
