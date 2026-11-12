# Reranker 集成的单元测试
# 不加载真实 CrossEncoder 模型：用 unittest.mock.patch 替身 get_reranker()，
# 让 predict() 返回固定分数，验证 rerank_chunks 的返回行为。
from unittest.mock import patch

import pytest

from app.rag.reranker import rerank_chunks


@patch("app.rag.reranker.get_reranker")
def test_rerank_chunks_returns_top_k(mock_get_reranker):
    # predict 返回固定的分数数组
    mock_get_reranker.return_value.predict.return_value = [
        0.1, 0.9, 0.5, 0.7, 0.3
    ]
    candidates = [
        {"document": f"doc{i}", "id": i} for i in range(5)
    ]

    result = rerank_chunks("问题", candidates, top_k=3)

    # 1) 返回长度 == top_k
    assert len(result) == 3

    # 2) 返回结果按分数降序，且取到的是分数最高的若干条
    scores = [c["rerank_score"] for c in result]
    assert scores == sorted(scores, reverse=True)
    assert scores == pytest.approx([0.9, 0.7, 0.5])

    # 3) 每条含 rerank_score，且类型为 float
    assert all("rerank_score" in c for c in result)
    assert all(isinstance(c["rerank_score"], float) for c in result)


@patch("app.rag.reranker.get_reranker")
def test_rerank_chunks_empty_candidates(mock_get_reranker):
    result = rerank_chunks("问题", [], top_k=3)

    assert result == []
    # 空候选直接短路，不应触发模型加载
    mock_get_reranker.assert_not_called()


@patch("app.rag.reranker.get_reranker")
def test_rerank_chunks_preserves_original_fields(mock_get_reranker):
    mock_get_reranker.return_value.predict.return_value = [0.2, 0.8]
    candidates = [
        {
            "document": "第一段文本",
            "distance": 0.12,
            "metadata": {"document_id": 1, "file_name": "a.txt"},
        },
        {
            "document": "第二段文本",
            "distance": 0.34,
            "metadata": {"document_id": 2, "file_name": "b.txt"},
        },
    ]
    original = [dict(c) for c in candidates]

    result = rerank_chunks("预算是多少", candidates, top_k=2)

    # 按分数降序：0.8 对应的「第二段文本」排在最前
    assert [c["document"] for c in result] == ["第二段文本", "第一段文本"]

    # document / distance / metadata 三个原始字段都还在，且值不变
    for item in result:
        assert "document" in item
        assert "distance" in item
        assert "metadata" in item
    assert result[0]["distance"] == 0.34
    assert result[0]["metadata"] == {
        "document_id": 2, "file_name": "b.txt"
    }

    # 返回的是浅拷贝，入参 dict 未被改动
    assert candidates == original
    assert all("rerank_score" not in c for c in candidates)
