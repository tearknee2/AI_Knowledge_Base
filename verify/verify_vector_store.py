from app.rag.vector_store import upsert_chunks

# 1.两条文本块的唯一ID
ids = [
    "test_doc_1_chunk_0",
    "test_doc_1_chunk_1",
]

# 2.两条测试文本
chunks = [
    "Python是一种编程语言",
    "Chroma可以保存文本和对应的向量。"
]

# 3.每条文本的来源信息
metadatas = [
    {
        "knowledge_base_id": 999,
        "document_id": 999,
        "chunk_index": 0
    },
    {
        "knowledge_base_id": 999,
        "document_id": 999,
        "chunk_index": 1
    },
]

# 4.两条测试向量
embeddings = [
    [0.1, 0.2, 0.3],
    [0.4, 0.5, 0.6]
]


upsert_chunks(
    ids,
    chunks,
    metadatas,
    embeddings
)


from app.rag.vector_store import init

client, collection = init()

result = collection.get(
    ids=ids,
    include=["documents", "metadatas"],
)

print("查询到的 ID：", result["ids"])
print("查询到的文本：", result["documents"])
print("查询到的元数据：", result["metadatas"])

assert len(result["ids"]) == 2
assert result["documents"] == chunks
assert result["metadatas"] == metadatas

print("Chroma 写入与查询验证通过")

# 再次写入相同的 ID
upsert_chunks(
    ids,
    chunks,
    metadatas,
    embeddings,
)

# 查询整个集合的记录数量
result = collection.get(
    include=["documents"]
)

print("集合当前记录数量：", len(result["ids"]))

assert len(result["ids"]) == 2

print("重复 upsert 验证通过")