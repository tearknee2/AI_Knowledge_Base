
from app.rag.vector_store import (
    init,
    upsert_chunks,
    delete_document_chunks,
)

document_id = 99998

client, collection = init()

# 清理可能遗留的测试数据
delete_document_chunks(document_id)

# 准备两个版本，每个版本各有 2 个文本块
ids = [
    "doc_99998_v1_chunk_0",
    "doc_99998_v1_chunk_1",
    "doc_99998_v2_chunk_0",
    "doc_99998_v2_chunk_1",
]

chunks = [
    "旧版本文本 0",
    "旧版本文本 1",
    "新版本文本 0",
    "新版本文本 1",
]

metadatas = [
    {"document_id": document_id, "version": "v1"},
    {"document_id": document_id, "version": "v1"},
    {"document_id": document_id, "version": "v2"},
    {"document_id": document_id, "version": "v2"},
]

embeddings = [[0.1] * 512 for _ in range(4)]

upsert_chunks(ids, chunks, metadatas, embeddings)

# 只删除 v1
delete_document_chunks(document_id, "v1")

result = collection.get(
    where={"document_id": document_id},
    include=["documents", "metadatas"],
)

print("剩余文本块：", result["documents"])
print("剩余元数据：", result["metadatas"])

assert len(result["ids"]) == 2
assert all(item["version"] == "v2" for item in result["metadatas"])
assert all(text.startswith("新版本") for text in result["documents"])

# 清理测试数据
delete_document_chunks(document_id)

print("PASS：按版本删除成功，v2 保留")
