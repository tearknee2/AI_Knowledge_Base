import os
from pathlib import Path

import torch
from dotenv import load_dotenv
from sentence_transformers import CrossEncoder

_rerank = None


def get_reranker():
    """懒加载CrossEncoder，首次调用时加载，后续复用"""
    global _rerank
    if _rerank is None:
        dot_env = Path(__file__).resolve().parent.parent.parent / ".env"
        load_dotenv(str(dot_env))

        model_path = os.getenv("BGE_RERANKER_PATH")
        if not model_path:
            raise ValueError("BGE_RERANKER_PATH environment variable not set")

        device = "cuda" if torch.cuda.is_available() else "cpu"
        _rerank = CrossEncoder(model_path, device=device)
    return _rerank

def rerank_chunks(question, candidates, top_k):
    """
    对候选chunk按reranker分数降序重排，返回前top_k
    :param question:
    :param candidates: list[dict]，每条至少包含“document"字段 (文本)
    :param top_k: 返回条数
    :return: list[dict]，保持原结构，可以附加“rerank_score”
    """
    if not candidates:
        return []

    pairs = [(question, c["document"]) for c in candidates]
    scores = get_reranker().predict(pairs)

    ranked = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    result = []
    for candidate, score in ranked[:top_k]:
        candidate = dict(candidate) # 浅拷贝，不改原始dict
        candidate["rerank_score"] = float(score)
        result.append(candidate)
    return result
    # return [{**c, "rerank_score":float(s)} for c,s in ranked[:top_k]]