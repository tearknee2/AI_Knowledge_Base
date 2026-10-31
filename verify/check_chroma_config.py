import chromadb
from app.rag.vector_store import init

_, collection = init()

print("Chroma 版本：", chromadb.__version__)
print("集合名称：", collection.name)
print("集合元数据：", collection.metadata)

configuration = getattr(collection, "configuration", None)
print("集合配置：", configuration)