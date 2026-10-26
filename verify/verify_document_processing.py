from app.core.database import SessionLocal
from app.repositories.document_repository import DocumentRepository
from app.services.document_processing_service import DocumentProcessingService


db = SessionLocal()
document_repository = DocumentRepository(db)
document_processing_service = DocumentProcessingService(document_repository)

count = document_processing_service.store_document_vectors(2)
print("写入chroma的文本块数量",count)

document = document_processing_service.query_document(2)
print("文档当前状态：",document.status)
print("文档错误信息：",document.error_message)

from app.rag.vector_store import init

client, collection = init()

result = collection.get(
    where={"document_id": 2},
    include=["documents", "metadatas"],
)

print("Chroma 实际记录数：", len(result["ids"]))

assert len(result["ids"]) == count
assert document.status == "COMPLETED"
assert document.error_message is None

print("PASS：文档处理与向量入库验证通过")

result = collection.get(
    where={"document_id":2},
    include=["documents", "metadatas","embeddings"],
)

# 1. 获取真实文档切分后的文本块
expected_chunks = document_processing_service.load_and_split_document(2)

# 2. 获取 Chroma 中保存的文本块
actual_chunks = result["documents"]

# 3. 打印对比
print("\n真实切分结果：")
for i, chunk in enumerate(expected_chunks):
    print(f"\n第 {i} 块：")
    print(repr(chunk))

print("\nChroma 中的实际结果：")
for i, chunk in enumerate(actual_chunks):
    print(f"\n第 {i} 块：")
    print(repr(chunk))

# 4. 自动比较
assert actual_chunks == expected_chunks

print("\nPASS：Chroma 中的文本块与真实切分结果完全一致")

assert len(result["documents"]) == 7
assert len(result["embeddings"][0]) == 512
assert all(
    len(embedding) == 512
    for embedding in result["embeddings"]
)
print(result["documents"][0])

print("文本块数量：", len(result["documents"]))
print("第一个向量的维度：", len(result["embeddings"][0]))
print("PASS：向量维度验证通过")


assert len(result["ids"]) == count
assert len(result["documents"]) == count
assert len({
    metadata["version"]
    for metadata in result["metadatas"]
}) == 1
#
# def mock_load_and_split_document(document_id: int):
#     """模拟文档读取或切分阶段失败。"""
#     raise ValueError("模拟文档切分失败")
#
#
# def main():
#     db = SessionLocal()
#
#     try:
#         # 1. 创建 Repository 和 Service
#         repository = DocumentRepository(db)
#         service = DocumentProcessingService(repository)
#
#         document_id = 2
#
#         # 2. 确认测试文档存在
#         document = service.query_document(document_id)
#         print("测试文档 ID：", document.id)
#         print("测试前状态：", document.status)
#
#         # 3. 临时替换文档读取与切分方法，模拟失败
#         service.load_and_split_document = mock_load_and_split_document
#
#         # 4. 执行处理流程，预期会抛出 ValueError
#         try:
#             service.store_document_vectors(document_id)
#             raise AssertionError("测试失败：预期发生异常，但没有发生")
#         except ValueError as exc:
#             if str(exc) != "模拟文档切分失败":
#                 raise
#
#             print("捕获到预期异常：", exc)
#
#         # 5. 重新查询数据库，验证失败状态是否已保存
#         db.expire_all()
#         document = service.query_document(document_id)
#
#         print("处理后状态：", document.status)
#         print("错误信息：", document.error_message)
#
#         assert document.status == "FAILED", (
#             f"状态验证失败，实际状态为：{document.status}"
#         )
#         assert document.error_message == "模拟文档切分失败", (
#             f"错误信息验证失败，实际内容为：{document.error_message}"
#         )
#
#         print("PASS：文档处理失败状态验证通过")
#
#     finally:
#         db.close()
#
#
# if __name__ == "__main__":
#     main()



# from app.rag.vector_store import init
#
# client, collection = init()
#
# result = collection.get(
#     where={"document_id": 2},
#     include=["documents", "metadatas"],
# )
#
# print("真实文档对应的向量记录数：", len(result["ids"]))
# print("第一条记录 ID：", result["ids"][0])
# print("第一条记录元数据：", result["metadatas"][0])
#
# assert len(result["ids"]) == 7
# assert all(
#     metadata["knowledge_base_id"] == 1
#     for metadata in result["metadatas"]
# )
# assert all(
#     metadata["document_id"] == 2
#     for metadata in result["metadatas"]
# )
#
# print("真实文档 Chroma 入库验证通过")

# # 查询真实文档记录
# document = document_processing_service.query_document(2)
#
# # 查看后续写入 Chroma 需要的字段
# print("文档 ID：", document.id)
# print("知识库 ID：", document.knowledge_base_id)
# print("文件名：", document.file_name)




# vectors = document_processing_service.vectorize_document(2)
#
# assert isinstance(vectors, list)
# assert len(vectors) == 7
# assert all(isinstance(vector, list) for vector in vectors)
# assert all(len(vector) > 0 for vector in vectors)
# assert len({len(vector) for vector in vectors}) == 1
#
# print(f"向量数量：{len(vectors)}")
# print(f"向量维度：{len(vectors[0])}")
# print("文档向量化验证通过")




# result = document_processing_service.load_and_split_document(2)
# print(result)

# print(f"文本块数量: {len(result)}")
#
# assert isinstance(result, list)
#
# for i, chunk in enumerate(result):
#     assert isinstance(chunk, str)
#     assert len(chunk) <= 500
#     print(f"第 {i+1} 块长度：{len(chunk)}")
#
# for i in range(len(result) - 1):
#     assert result[i][-50:] == result[i+1][:50]
#
# print("文本加载与分块验证通过")