# rag.service
from app.core.config import ENABLE_RERANK
from app.rag.embedding import embed_texts
from app.rag.reranker import rerank_chunks
from app.rag.vector_store import search_chunks
from app.rag.generation import build_context,generate_answer
from app.repositories.document_repository import DocumentRepository


async def answer_question(
    question: str,
    knowledge_base_id: int,
    document_repository: DocumentRepository,
    history_messages: list[dict],
    n_results: int = 4,
) -> dict:
    """完成一次完整的RAG问答"""

    # 1.将question转换成向量
    question_vectors = embed_texts([question])
    query_embedding = question_vectors[0]

    candidate_count = max(n_results * 5, 20)
    # 2.从指定知识库检索文本块
    result = search_chunks(
        query_embedding,
        knowledge_base_id,
        candidate_count
    )

    # 3.提取检索到的文本块、元数据和距离
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

    # 创建筛选结果列表
    completed_document_ids = set(
        document_repository.get_completed_document_ids(
            knowledge_base_id=knowledge_base_id,
        )
    )

    filtered_results = []

    # 遍历并筛选
    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        metadata = metadata or {}
        document_id = metadata.get("document_id")

        if document_id not in completed_document_ids:
            continue

        filtered_results.append(
            {
                "document":document,
                "metadata":metadata,
                "distance":distance
            }
        )

    if ENABLE_RERANK:
        filtered_results = rerank_chunks(question, filtered_results, n_results)
    else:
        filtered_results = filtered_results[:n_results]

    # 从筛选结果中取出后续需要的数据
    documents = [
        item["document"] for item in filtered_results
    ]
    metadatas = [
        item["metadata"] for item in filtered_results
    ]
    distances = [
        item["distance"] for item in filtered_results
    ]


    # 4.如果没有检索到文本块，直接返回无相关信息的结果
    if not documents:
        return {
            "answer":"知识库无相关结果",
            "sources":[],
        }

    # 5.组织知识上下文
    context = build_context(documents)

    # 6.调用大模型生成答案
    answer = await generate_answer(
        query=question,
        context=context,
        history_messages=history_messages,
    )

    # 7.整理每个命中文本块的来源信息
    sources = []

    for content, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):
        metadata = metadata or {}

        sources.append({
            "content":content,
            "file_name":metadata.get("file_name"),
            "document_id":metadata.get("document_id"),
            "chunk_index":metadata.get("chunk_index"),
            "distance":distance
        })
    return {
        "answer": answer,
        "sources": sources
    }