from app.rag.embedding import embed_texts
from app.rag.vector_store import search_chunks

question1 = "星河计划的项目预算是多少？"
query_vector1 = embed_texts([question1])

chunks_q1 = search_chunks(query_vector1[0], 12, 5)

documents = chunks_q1["documents"][0]
distances = chunks_q1["distances"][0]

for document,distance in zip(documents, distances):
    print("文本:", document)
    print("距离:", distance)
# print("nihao")
# print("字典的键有：", chunks_q1.keys())
# print("字典的长度是：", len(chunks_q1))
