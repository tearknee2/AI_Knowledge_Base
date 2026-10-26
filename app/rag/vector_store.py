# 把"写入向量数据库"封装成独立能力
import chromadb

_client = None
_collection = None

def init():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path="./chroma_test_db"
        )
        _collection = _client.get_or_create_collection(
            name="knowledge_chunks_bge_test"
        )
    return _client, _collection

def upsert_chunks(
    ids: list[str],
    chunks: list[str],
    metadatas: list[dict],
    embeddings: list[list[float]]
):
    # 创建持久化客户端
    client, collection = init()
    collection.upsert(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
        embeddings=embeddings,
    )


def delete_document_chunks(
    document_id: int,
    version: str | None = None,
):
    """删除指定文档在chroma中的文本块,传入version时只删除指定版本。"""
    client, collection = init()

    where = {"document_id": document_id}
    if version is not None:
        where = {
            "$and":[
                {"document_id": document_id},
                {"version": version}
            ]
        }
    collection.delete(where=where)