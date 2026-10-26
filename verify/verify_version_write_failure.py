from app.rag.vector_store import init, upsert_chunks

document_id = 99996

client, collection = init()

# 1. 清理测试数据
collection.delete(where={"document_id": document_id})

# 2. 写入旧版本
upsert_chunks(
    ids=["doc_99996_v1_chunk_0"],
    chunks=["旧版本的有效文本"],
    metadatas=[
        {"document_id": document_id, "version": "v1"}
    ],
    embeddings=[[0.1] * 512],
)

before = collection.get(
    where={"document_id": document_id},
    include=["documents", "metadatas"],
)

print("新版本写入前：", before["documents"])

# 3. 模拟新版本写入失败
try:
    raise RuntimeError("模拟新版本写入失败")
except RuntimeError as exc:
    print("捕获异常：", exc)

# 4. 检查旧版本是否保留
after = collection.get(
    where={"document_id": document_id},
    include=["documents", "metadatas"],
)

print("新版本写入失败后：", after["documents"])

assert len(after["ids"]) == 1
assert after["metadatas"][0]["version"] == "v1"
assert after["documents"][0] == "旧版本的有效文本"

# 5. 清理测试数据
collection.delete(where={"document_id": document_id})

print("PASS：模拟新版本写入失败时，旧版本仍然保留")