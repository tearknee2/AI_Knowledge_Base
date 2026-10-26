
from app.rag.vector_store import (
    init,
    upsert_chunks,
    delete_document_chunks,
)

document_id = 2
client, collection = init()

# 1. 准备 7 条模拟文本块
old_chunks = [f"旧文本块 {i}" for i in range(7)]
old_ids = [f"doc_{document_id}_chunk_{i}" for i in range(7)]
old_metadatas = [
    {
        "document_id": document_id,
        "knowledge_base_id": 1,
        "chunk_index": i,
        "file_name": "test.txt",
    }
    for i in range(7)
]
old_embeddings = [[0.1] * 512 for _ in range(7)]

# 2. 先写入 7 条模拟记录
upsert_chunks(old_ids, old_chunks, old_metadatas, old_embeddings)

before = collection.get(
    where={"document_id": document_id},
    include=["documents", "metadatas"],
)
print("第一次写入后的记录数：", len(before["ids"]))

# 3. 模拟重新处理：先删除旧数据，再写入 5 条新数据
delete_document_chunks(document_id)

new_chunks = [f"新文本块 {i}" for i in range(5)]
new_ids = [f"doc_{document_id}_chunk_{i}" for i in range(5)]
new_metadatas = [
    {
        "document_id": document_id,
        "knowledge_base_id": 1,
        "chunk_index": i,
        "file_name": "test.txt",
    }
    for i in range(5)
]
new_embeddings = [[0.2] * 512 for _ in range(5)]

upsert_chunks(new_ids, new_chunks, new_metadatas, new_embeddings)

# 4. 查询最终记录
after = collection.get(
    where={"document_id": document_id},
    include=["documents", "metadatas"],
)

print("重新处理后的记录数：", len(after["ids"]))
print("最终文本块：", after["documents"])

assert len(before["ids"]) == 7
assert len(after["ids"]) == 5
assert all(text.startswith("新文本块") for text in after["documents"])

print("PASS：重新处理后没有残留旧文本块")
