from app.rag.vector_store import (
    init,
    upsert_chunks,
    delete_document_chunks,
)

document_id = 99999

client, collection = init()

# 1. 准备 3 条旧向量记录
old_chunks = [f"旧文本块 {i}" for i in range(3)]
old_ids = [
    f"doc_{document_id}_chunk_{i}"
    for i in range(3)
]
old_metadatas = [
    {
        "document_id": document_id,
        "knowledge_base_id": 1,
        "chunk_index": i,
        "file_name": "failure_test.txt",
    }
    for i in range(3)
]
old_embeddings = [[0.1] * 512 for _ in range(3)]

# 清理可能遗留的测试数据
delete_document_chunks(document_id)

upsert_chunks(
    old_ids,
    old_chunks,
    old_metadatas,
    old_embeddings,
)

before = collection.get(
    where={"document_id": document_id},
    include=["documents"],
)

print("旧向量数量：", len(before["ids"]))
assert len(before["ids"]) == 3

# 2. 模拟新向量写入失败
try:
    # 模拟当前业务流程：先删除旧向量
    delete_document_chunks(document_id)

    # 模拟写入新向量时发生异常
    raise RuntimeError("模拟 Chroma 新向量写入失败")

except RuntimeError as exc:
    print("捕获异常：", exc)

# 3. 检查失败后的数据状态
after = collection.get(
    where={"document_id": document_id},
    include=["documents"],
)

print("写入失败后的向量数量：", len(after["ids"]))

assert len(after["ids"]) == 0

print("PASS：成功复现旧向量丢失的风险")