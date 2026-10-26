from app.rag.vector_store import init, upsert_chunks

document_id = 99995
version = "v2"

client, collection = init()

# 1. 清理之前遗留的测试数据
collection.delete(where={"document_id": document_id})

# 2. 准备旧版本、新版本和没有版本号的历史向量
ids = [
    "doc_99995_v1_chunk_0",
    "doc_99995_v2_chunk_0",
    "doc_99995_legacy_chunk_0",
]

chunks = [
    "旧版本文本",
    "新版本文本",
    "历史遗留文本",
]

metadatas = [
    {"document_id": document_id, "version": "v1"},
    {"document_id": document_id, "version": "v2"},
    {"document_id": document_id},
]

embeddings = [[0.1] * 512 for _ in range(3)]

upsert_chunks(ids, chunks, metadatas, embeddings)

# 3. 查询当前文档的全部向量
all_vectors = collection.get(
    where={"document_id": document_id},
    include=["metadatas"],
)

# 4. 模拟当前版本清理逻辑
old_ids = [
    vector_id
    for vector_id, metadata in zip(
        all_vectors["ids"],
        all_vectors["metadatas"],
    )
    if metadata is None or metadata.get("version") != version
]

if old_ids:
    collection.delete(ids=old_ids)

# 5. 检查清理结果
result = collection.get(
    where={"document_id": document_id},
    include=["documents", "metadatas"],
)

print("剩余文本：", result["documents"])
print("剩余元数据：", result["metadatas"])

assert len(result["ids"]) == 1
assert result["documents"] == ["新版本文本"]
assert result["metadatas"][0]["version"] == version

# 6. 清理测试数据
collection.delete(where={"document_id": document_id})

print("PASS：新版本保留，旧版本和历史无版本记录均已清理")