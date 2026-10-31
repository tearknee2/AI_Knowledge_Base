from app.rag.vector_store import init

client,collection = init()

result = collection.get(
    where={"document_id":{"$eq":9}},
    include=["documents", "metadatas"]
)
print(len(result["ids"]))
for i,doc in enumerate(result["documents"]):
    print(f"===== chunk {i} =====")
    print(doc)
