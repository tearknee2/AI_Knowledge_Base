from app.rag.vector_store import init, upsert_chunks

document_id = 99997

client, collection = init()

# 清理上次测试遗留数据
collection.delete(where={"document_id": document_id})

# 准备两个版本的测试数据
ids = [
    "filter_test_v1_0",
    "filter_test_v2_0",
]

chunks = [
    "旧版本测试文本",
    "新版本测试文本",
]

metadatas = [
    {"document_id": document_id, "version": "v1"},
    {"document_id": document_id, "version": "v2"},
]

embeddings = [[0.1] * 512 for _ in range(2)]

upsert_chunks(ids, chunks, metadatas, embeddings)

# 模拟当前版本是 v2，查询不属于 v2 的记录
collection.delete(
    where={
        "$and": [
            {"document_id": document_id},
            {"version": {"$ne": "v2"}},
        ]
    }
)

result = collection.get(
    where={"document_id": document_id},
    include=["documents", "metadatas"],
)

print("剩余记录：", result["documents"])
print("剩余元数据：", result["metadatas"])

assert len(result["ids"]) == 1
assert result["metadatas"][0]["version"] == "v2"

# 清理测试数据
collection.delete(where={"document_id": document_id})

print("PASS：当前 Chroma 支持该版本过滤条件")