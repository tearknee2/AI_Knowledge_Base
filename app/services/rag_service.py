from app.rag.embedding import embed_texts
from app.rag.vector_store import search_chunks
from app.rag.generation import build_context,generate_answer

async def answer_question(
    question: str,
    knowledge_base_id: int,
    n_results: int = 4,
) -> dict:
    """完成一次完整的RAG问答"""
    # 1.将question转换成向量
    question_vectors = embed_texts([question])
    query_embedding = question_vectors[0]

    # 2.从指定知识库检索文本块
    result = search_chunks(
        query_embedding,
        knowledge_base_id,
        n_results)

    # 3.提取检索到的文本块、元数据和距离
    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]

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
        context=context
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