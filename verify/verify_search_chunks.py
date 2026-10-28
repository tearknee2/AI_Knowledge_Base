from app.rag.embedding import embed_texts
from app.rag.vector_store import search_chunks,upsert_chunks

# 1.准备两条测试文本
chunks = [
    "Python 是一种解释型编程语言，具有语法简洁、生态丰富等特点。",
    "Redis 是一种支持多种数据结构的内存数据库，常用于缓存。",
]

# 2.给两条文本添加元数据
metadatas = [
    {"knowledge_base_id": 4, "document_id": 101},
    {"knowledge_base_id": 4, "document_id": 102},
]

# 3.生成向量
embeddings = embed_texts(chunks)

# 4.为每条文本准备唯一ID
ids = [
    "verify_python_101",
    "verify_redis_102"
]

# 5.写入chroma
upsert_chunks(ids, chunks, metadatas, embeddings)

print("测试数据写入完成")

# 6.准备查询问题
query = ["Python有哪些特点？"]

# 7.将问题转换为向量
vectors = embed_texts(query)

# 8.在知识库4中检索，最多返回2条
query_result = search_chunks(
    vectors[0],
    4,
    4
)

# 9. 打印检索结果
print("检索到的文本：")
print(query_result["documents"])

print("对应的文档 ID：")
print(query_result["metadatas"])

print("距离：")
print(query_result["distances"])