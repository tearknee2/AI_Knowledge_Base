# 端到端集成测试：上传 TXT -> 结构化切分 -> Embedding -> Chroma 写入
import io
import os
import uuid
from pathlib import Path
from types import SimpleNamespace

import chromadb
import pytest
from dotenv import load_dotenv
from transformers import AutoTokenizer

from app.models.document import Document
from app.models.knowledge_base import KnowledgeBase
from app.models.user import User
from app.rag import vector_store
from app.rag.chunk_size_overlap import (
    build_chunk_embedding_text,
    group_structured_documents,
    merge_paragraph_blocks,
    parse_structured_document,
    split_structured_group,
)
from app.rag.txt_loader import load_txt
from app.repositories.document_repository import DocumentRepository
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.services import document_processing_service
from app.services.document_processing_service import DocumentProcessingService
from app.services.document_service import DocumentService
from app.services.knowledge_base_service import KnowledgeBaseService

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

ATTENDANCE_SENTENCE = "员工应当遵守考勤制度，按时上下班，并完成每日考勤登记。"
LEAVE_SENTENCE = "员工请假应当提前提交申请，并经负责人审批。"

DOCUMENT_TEXT = (
    "# 员工管理制度\n"
    "\n"
    "## 考勤管理\n"
    "\n"
    "**第一条 考勤要求**\n"
    "\n"
    + ATTENDANCE_SENTENCE * 20
    + "\n"
    "\n"
    "**第二条 请假要求**\n"
    "\n"
    + LEAVE_SENTENCE * 10
    + "\n"
)


class FakeUploadFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = io.BytesIO(content.encode("utf-8"))


@pytest.fixture(scope="module")
def tokenizer():
    model_path = os.getenv("BGE_MODEL_PATH")
    if not model_path:
        pytest.skip("BGE_MODEL_PATH 未配置")
    return AutoTokenizer.from_pretrained(model_path, local_files_only=True)


@pytest.fixture()
def chroma_collection(monkeypatch):
    client = chromadb.EphemeralClient()
    collection = client.get_or_create_collection(
        name=f"integration_{uuid.uuid4().hex}"
    )
    monkeypatch.setattr(vector_store, "init", lambda: (client, collection))
    monkeypatch.setattr(
        document_processing_service,
        "init",
        lambda: (client, collection),
    )
    return collection


@pytest.fixture()
def env(db_session, tokenizer, chroma_collection, monkeypatch):
    user = User(username="integration-user", password_hash="test-hash")
    db_session.add(user)
    db_session.commit()

    knowledge_base = KnowledgeBase(
        user_id=user.id,
        name="集成测试库",
        description=None,
        status="ACTIVE",
    )
    db_session.add(knowledge_base)
    db_session.commit()

    repository = DocumentRepository(db_session)
    processing_service = DocumentProcessingService(
        repository,
        tokenizer=tokenizer,
    )

    embedding_inputs = []

    def fake_embed_texts(texts, batch_size=256):
        embedding_inputs.extend(texts)
        return [[float(len(text)), 1.0, 2.0] for text in texts]

    monkeypatch.setattr(
        document_processing_service,
        "embed_texts",
        fake_embed_texts,
    )

    statuses = []
    original_update_status = repository.update_status

    def tracked_update_status(*args, **kwargs):
        status = args[1] if len(args) > 1 else kwargs.get("status")
        statuses.append(status)
        return original_update_status(*args, **kwargs)

    monkeypatch.setattr(
        repository,
        "update_status",
        tracked_update_status,
    )

    knowledge_base_service = KnowledgeBaseService(
        KnowledgeBaseRepository(db_session)
    )
    document_service = DocumentService(
        repository,
        knowledge_base_service,
        processing_service,
    )

    yield SimpleNamespace(
        db_session=db_session,
        repository=repository,
        processing_service=processing_service,
        document_service=document_service,
        user=user,
        knowledge_base=knowledge_base,
        collection=chroma_collection,
        embedding_inputs=embedding_inputs,
        statuses=statuses,
    )

    db_session.expire_all()
    for document in db_session.query(Document).all():
        file_path = Path(document.file_path)
        file_path.unlink(missing_ok=True)
        try:
            file_path.parent.rmdir()
        except OSError:
            pass


def upload_document(env):
    document = env.document_service.upload_document(
        env.knowledge_base.id,
        FakeUploadFile("structured.txt", DOCUMENT_TEXT),
        user_id=env.user.id,
    )
    env.db_session.expire_all()
    return env.repository.get_by_id(document.id)


def expected_chunks(file_path, tokenizer):
    text = load_txt(str(file_path))
    blocks = merge_paragraph_blocks(parse_structured_document(text))
    groups = group_structured_documents(blocks)
    return [
        chunk
        for group in groups
        for chunk in split_structured_group(group, tokenizer)
    ]


def get_records(collection, document_id):
    result = collection.get(
        where={"document_id": document_id},
        include=["documents", "metadatas", "embeddings"],
    )
    records = {}
    for chunk_id, document, metadata, embedding in zip(
        result["ids"],
        result["documents"],
        result["metadatas"],
        result["embeddings"],
    ):
        records[metadata["chunk_index"]] = {
            "id": chunk_id,
            "document": document,
            "metadata": metadata,
            "embedding": embedding,
        }
    return records


def test_upload_document_structured_pipeline_end_to_end(env):
    document = upload_document(env)

    # 1. 状态流转与最终状态
    assert env.statuses == [
        "PARSING",
        "CHUNKING",
        "EMBEDDING",
        "COMPLETED",
    ]
    assert document.status == "COMPLETED"
    assert document.error_message is None

    # 2. 服务确实使用结构化 Chunking
    chunks = expected_chunks(document.file_path, env.processing_service.tokenizer)
    assert len(chunks) >= 2
    assert any(chunk["clause_title"] for chunk in chunks)
    assert any(len(chunk["section_path"]) >= 2 for chunk in chunks)

    # 3. Chroma 中的正文、向量与 metadata
    records = get_records(env.collection, document.id)
    assert set(records) == set(range(len(chunks)))

    expected_embedding_texts = [
        build_chunk_embedding_text(chunk)
        for chunk in chunks
    ]
    assert env.embedding_inputs == expected_embedding_texts

    for index, chunk in enumerate(chunks):
        record = records[index]
        embedding_text = expected_embedding_texts[index]

        # documents 保存原始正文，而不是 embedding_text
        assert record["document"] == chunk["text"]
        assert record["document"] != embedding_text
        assert not record["document"].startswith(
            " > ".join(chunk["section_path"])
        )

        # 向量由 embedding_text 生成
        assert list(record["embedding"]) == pytest.approx(
            [float(len(embedding_text)), 1.0, 2.0]
        )

        # metadata 保留现有必要字段
        assert record["metadata"]["knowledge_base_id"] == env.knowledge_base.id
        assert record["metadata"]["document_id"] == document.id
        assert record["metadata"]["chunk_index"] == index
        assert record["metadata"]["file_name"] == "structured.txt"
        assert record["metadata"]["section_path"] == " > ".join(
            chunk["section_path"]
        )
        assert record["metadata"]["version"]

    # 4. 同文档重新处理：旧版本向量应被清理
    first_version = records[0]["metadata"]["version"]
    first_ids = {record["id"] for record in records.values()}

    env.processing_service.store_document_vectors(document.id)
    env.db_session.expire_all()
    document = env.repository.get_by_id(document.id)

    assert document.status == "COMPLETED"
    assert env.statuses[4:] == [
        "PARSING",
        "CHUNKING",
        "EMBEDDING",
        "COMPLETED",
    ]

    new_records = get_records(env.collection, document.id)
    assert len(new_records) == len(chunks)

    new_versions = {
        record["metadata"]["version"]
        for record in new_records.values()
    }
    assert len(new_versions) == 1
    assert first_version not in new_versions
    assert first_ids.isdisjoint(
        {record["id"] for record in new_records.values()}
    )


def test_processing_failure_marks_failed_and_keeps_old_vectors(env, monkeypatch):
    document = upload_document(env)
    before = get_records(env.collection, document.id)
    before_ids = {record["id"] for record in before.values()}
    before_versions = {
        record["metadata"]["version"]
        for record in before.values()
    }
    assert document.status == "COMPLETED"

    def failing_embed_texts(texts, batch_size=256):
        raise ValueError("模拟向量生成失败")

    monkeypatch.setattr(
        document_processing_service,
        "embed_texts",
        failing_embed_texts,
    )

    with pytest.raises(ValueError, match="模拟向量生成失败"):
        env.processing_service.store_document_vectors(document.id)

    env.db_session.expire_all()
    document = env.repository.get_by_id(document.id)

    assert document.status == "FAILED"
    assert document.error_message == "模拟向量生成失败"
    assert env.statuses[-1] == "FAILED"

    after = get_records(env.collection, document.id)
    assert {record["id"] for record in after.values()} == before_ids
    assert {
        record["metadata"]["version"]
        for record in after.values()
    } == before_versions
    assert {
        record["document"]
        for record in after.values()
    } == {
        record["document"]
        for record in before.values()
    }
