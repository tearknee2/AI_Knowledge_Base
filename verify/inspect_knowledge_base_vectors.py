from app.rag.vector_store import init

client, collection = init()

result = collection.get(
    where={"document_id": 7},
    include=["documents", "metadatas"],
)

print("向量数量：", len(result["ids"]))

for vector_id, document, metadata in zip(
    result["ids"],
    result["documents"],
    result["metadatas"],
):
    print("向量 ID：", vector_id)
    print("文本块：", document)
    print("元数据：", metadata)
    print("-" * 40)