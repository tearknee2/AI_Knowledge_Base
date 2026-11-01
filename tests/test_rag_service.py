import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.services import rag_service


def test_answer_question_only_uses_completed_documents(monkeypatch):
    # 1. 模拟向量检索：返回三个不同状态文档的文本块
    monkeypatch.setattr(
        rag_service,
        "embed_texts",
        lambda texts: [[0.1, 0.2, 0.3]],
    )

    monkeypatch.setattr(
        rag_service,
        "search_chunks",
        lambda *args, **kwargs: {
            "ids": [["chunk_1", "chunk_2", "chunk_3"]],
            "documents": [
                [
                    "已完成文档的内容",
                    "处理失败文档的内容",
                    "正在处理文档的内容",
                ]
            ],
            "metadatas": [
                [
                    {"document_id": 1, "file_name": "completed.txt"},
                    {"document_id": 2, "file_name": "failed.txt"},
                    {"document_id": 3, "file_name": "processing.txt"},
                ]
            ],
            "distances": [[0.1, 0.2, 0.3]],
        },
    )

    # 2. 模拟 Repository：只有文档 1 已完成
    document_repository = MagicMock()
    document_repository.get_completed_document_ids.return_value = [1]

    # 3. 监控上下文构建和大模型调用
    build_context_mock = MagicMock(return_value="已完成文档的内容")
    generate_answer_mock = AsyncMock(return_value="测试答案")

    monkeypatch.setattr(
        rag_service, "build_context", build_context_mock
    )
    monkeypatch.setattr(
        rag_service, "generate_answer", generate_answer_mock
    )

    # 4. 执行被测函数
    result = asyncio.run(
        rag_service.answer_question(
            question="测试问题",
            knowledge_base_id=12,
            document_repository=document_repository,
            n_results=4,
        )
    )

    # 5. 验收：上下文只包含已完成文档
    build_context_mock.assert_called_once_with(
        ["已完成文档的内容"]
    )

    # 验收：大模型只接收到已完成文档构建的上下文
    generate_answer_mock.assert_awaited_once_with(
        query="测试问题",
        context="已完成文档的内容",
    )

    # 验收：来源只包含已完成文档
    assert len(result["sources"]) == 1
    assert result["sources"][0]["document_id"] == 1
    assert result["sources"][0]["file_name"] == "completed.txt"
    assert result["answer"] == "测试答案"

def test_answer_question_skips_llm_when_no_completed_documents(monkeypatch):
    # 1. 模拟向量检索
    monkeypatch.setattr(
        rag_service,
        "embed_texts",
        lambda texts: [[0.1, 0.2, 0.3]],
    )

    monkeypatch.setattr(
        rag_service,
        "search_chunks",
        lambda *args, **kwargs: {
            "ids": [["chunk_1", "chunk_2"]],
            "documents": [["失败文档内容", "处理中内容"]],
            "metadatas": [
                [
                    {"document_id": 2, "file_name": "failed.txt"},
                    {"document_id": 3, "file_name": "processing.txt"},
                ]
            ],
            "distances": [[0.1, 0.2]],
        },
    )

    # 2. 模拟没有任何已完成文档
    document_repository = MagicMock()
    document_repository.get_completed_document_ids.return_value = []

    # 3. 监控上下文构建和大模型调用
    build_context_mock = MagicMock()
    generate_answer_mock = AsyncMock()

    monkeypatch.setattr(
        rag_service, "build_context", build_context_mock
    )
    monkeypatch.setattr(
        rag_service, "generate_answer", generate_answer_mock
    )

    # 4. 执行被测函数
    result = asyncio.run(
        rag_service.answer_question(
            question="测试问题",
            knowledge_base_id=12,
            document_repository=document_repository,
            n_results=4,
        )
    )

    assert result["answer"] == "知识库无相关结果"
    assert result["sources"] == []
    build_context_mock.assert_not_called()
    generate_answer_mock.assert_not_called()


def test_answer_question_handles_empty_search_results(monkeypatch):
    # 1. 模拟向量检索
    monkeypatch.setattr(
        rag_service,
        "embed_texts",
        lambda texts: [[0.1, 0.2, 0.3]],
    )

    monkeypatch.setattr(
        rag_service,
        "search_chunks",
        lambda *args, **kwargs: {
            "ids": [[]],
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }
    )

    # 2. 模拟没有任何已完成文档
    document_repository = MagicMock()
    document_repository.get_completed_document_ids.return_value = []

    # 3. 监控上下文构建和大模型调用
    build_context_mock = MagicMock()
    generate_answer_mock = AsyncMock()

    monkeypatch.setattr(
        rag_service, "build_context", build_context_mock
    )
    monkeypatch.setattr(
        rag_service, "generate_answer", generate_answer_mock
    )

    # 4. 执行被测函数
    result = asyncio.run(
        rag_service.answer_question(
            question="测试问题",
            knowledge_base_id=12,
            document_repository=document_repository,
            n_results=4,
        )
    )

    assert result["answer"] == "知识库无相关结果"
    assert result["sources"] == []
    build_context_mock.assert_not_called()
    generate_answer_mock.assert_not_called()

def test_answer_question_fetches_extra_candidates(monkeypatch):
    monkeypatch.setattr(
        rag_service,
        "embed_texts",
        lambda texts: [[0.1, 0.2, 0.3]],
    )

    # 模拟前 4 个结果只有 2 个已完成文档，
    # 后续结果中还有 2 个已完成文档。
    search_result = {
        "ids": [[f"chunk_{i}" for i in range(1, 7)]],
        "documents": [[f"文档内容{i}" for i in range(1, 7)]],
        "metadatas": [[
            {"document_id": 1, "file_name": "doc1.txt"},
            {"document_id": 2, "file_name": "doc2.txt"},
            {"document_id": 3, "file_name": "doc3.txt"},
            {"document_id": 4, "file_name": "doc4.txt"},
            {"document_id": 5, "file_name": "doc5.txt"},
            {"document_id": 6, "file_name": "doc6.txt"},
        ]],
        "distances": [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6]],
    }

    search_mock = MagicMock(return_value=search_result)
    monkeypatch.setattr(rag_service, "search_chunks", search_mock)

    document_repository = MagicMock()
    document_repository.get_completed_document_ids.return_value = [1, 5, 6, 4]

    build_context_mock = MagicMock(
        return_value="有效文档上下文"
    )
    generate_answer_mock = AsyncMock(return_value="测试答案")

    monkeypatch.setattr(
        rag_service, "build_context", build_context_mock
    )
    monkeypatch.setattr(
        rag_service, "generate_answer", generate_answer_mock
    )

    result = asyncio.run(
        rag_service.answer_question(
            question="测试问题",
            knowledge_base_id=12,
            document_repository=document_repository,
            n_results=4,
        )
    )

    # 检查候选数量至少为 20
    assert search_mock.call_args.args[2] == 20

    # 检查过滤后能保留 4 个有效来源
    assert len(result["sources"]) == 4
    assert [
        source["document_id"] for source in result["sources"]
    ] == [1, 4, 5, 6]

    build_context_mock.assert_called_once_with([
        "文档内容1",
        "文档内容4",
        "文档内容5",
        "文档内容6",
    ])
    generate_answer_mock.assert_awaited_once()