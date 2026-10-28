# from app.schemas.chat import ChatRequest, ChatSource, ChatResponse
#
#
# request = ChatRequest(
#     question="公司什么时候举行项目复盘会议？"
# )
#
# response = ChatResponse(
#     question=request.question,
#     answer="公司每周五下午举行项目复盘会议。",
#     sources=[
#         ChatSource(
#             content="公司每周五下午举行项目复盘会议。",
#             file_name= "project_rules.md",
#             document_id= 9001,
#             chunk_index= 0,
#             distance=0.34,)
#     ]
# )
#
# print(response.model_dump())
from app.rag.embedding import embed_texts
from app.rag.vector_store import search_chunks

# 1.定义查询问题
query = ["星河计划的项目代号是什么"]

# 2.将问题转换为向量
query_vectors = embed_texts(query)

# 3.在知识库12中检索最多4个文本块
result = search_chunks(
    query_embedding=query_vectors[0],
    knowledge_base_id=12,
    n_results=4
)

# 4. 打印检索结果
print(result["documents"])
print(result["metadatas"])
print(result["distances"])