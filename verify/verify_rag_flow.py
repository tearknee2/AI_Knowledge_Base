
import asyncio

from app.rag.embedding import embed_texts
from app.rag.vector_store import upsert_chunks
from app.services.rag_service import answer_question


async def main():
    # 1. 准备独立的测试数据
    knowledge_base_id = 9876

    chunks = [
        "公司每周五下午举行项目复盘会议。",
        "项目复盘会议由项目负责人主持。",
    ]

    metadatas = [
        {
            "knowledge_base_id": knowledge_base_id,
            "document_id": 9001,
            "file_name": "project_rules.md",
            "chunk_index": 0,
        },
        {
            "knowledge_base_id": knowledge_base_id,
            "document_id": 9001,
            "file_name": "project_rules.md",
            "chunk_index": 1,
        },
    ]

    ids = [
        "verify_rag_flow_9876_0",
        "verify_rag_flow_9876_1",
    ]

    # 2. 将测试文本转换成向量
    embeddings = embed_texts(chunks)

    # 3. 将文本、元数据和向量写入向量数据库
    upsert_chunks(
        ids=ids,
        chunks=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print("测试数据写入完成")

    # 4. 调用完整 RAG 链路
    result = await answer_question(
        question="公司什么时候举行项目复盘会议？",
        knowledge_base_id=knowledge_base_id,
        n_results=2,
    )

    # 5. 检查并打印最终结果
    print("\n最终答案：")
    print(result["answer"])

    print("\n答案来源：")
    for source in result["sources"]:
        print(source)

    assert isinstance(result["answer"], str)
    assert result["answer"].strip()
    assert len(result["sources"]) > 0
    assert all(
        source["file_name"] == "project_rules.md"
        for source in result["sources"]
    )

    print("\nRAG 链路验证通过！")


if __name__ == "__main__":
    asyncio.run(main())
