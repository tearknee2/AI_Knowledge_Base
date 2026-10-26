from app.rag.vector_store import init

document_id = 5

client, collection = init()
print("Chroma 数据库目录：", client.get_settings().persist_directory)
print("当前集合名称：", collection.name)
print("当前集合总记录数：", collection.count())
# result = collection.get(
#     where={"document_id": 3},
#     include=["documents", "metadatas"],
# )
#
# print("文档 ID：", 3)
# print("查询到的文本块数量：", len(result["ids"]))
# print("当前集合总记录数：", collection.count())
# print("查询到的元数据：", result["metadatas"])
result = collection.get(
    where={"document_id": document_id},
    include=["documents", "embeddings", "metadatas"],
)

print("文档 ID：", document_id)
print("文本块数量：", len(result["ids"]))

if len(result["embeddings"]) > 0:
    print("向量维度：", len(result["embeddings"][0]))

print("文本块内容：", result["documents"])
print("元数据：", result["metadatas"])

assert len(result["ids"]) > 0, "没有找到该文档的向量记录"
assert all(
    len(vector) == 512
    for vector in result["embeddings"]
), "存在维度不是 512 的向量"

print("PASS：向量记录存在，且向量维度均为 512")