from sentence_transformers import SentenceTransformer
import chromadb

client = chromadb.PersistentClient(
    path="./chroma_practice_db"
)
collection = client.get_or_create_collection(
    name="knowledge_chunks_bge"
)

# print("Chroma 集合创建成功")
# print("集合名称：", collection.name)

model_path = (
    r"C:\Users\tear_knee\.cache\huggingface\hub"
    r"\models--BAAI--bge-small-zh-v1.5"
    r"\snapshots\7999e1d3359715c523056ef9478215996d62a620"
)
model = SentenceTransformer(model_path)



chunks = [
    "Python 是一种编程语言。",
    "Python 支持多种编程范式。"
]
knowledge_base_id = 3
document_id = 27
file_name = "python_intro.txt"

ids = [f"doc_{document_id}_chunk_{i}"
       for i in range(len(chunks))
]
documents = chunks
metadatas = [
    {
        "knowledge_base_id": knowledge_base_id,
        "document_id": document_id,
        "chunk_index": i,
        "file_name": file_name,
    }
    for i in range(len(chunks))
]

embeddings = model.encode(chunks)

collection.upsert(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
    embeddings=embeddings.tolist(),
)

result = collection.get(
    ids=ids,
    include=['documents','metadatas']
)
# print("写入完成")
# print("文本", result['documents'])
# print("元数据", result['metadatas'])
# print("记录数量", len(result['ids']))

query_text = "Python有那些特点？"
query_embedding= model.encode([query_text])
query_result = collection.query(
    query_embeddings=query_embedding.tolist(),
    n_results=2,
    include=['documents','metadatas','distances'],
    where={"knowledge_base_id": 3},
)
print("检索文本:",query_result['documents'])
print("检索元数据:",query_result['metadatas'])
print("向量距离:",query_result['distances'])