# 把"写入向量数据库"封装成独立能力
import chromadb
from dotenv import load_dotenv
import os

load_dotenv()
CHROMA_PATH = os.getenv("CHROMA_PATH")

_client = None
_collection = None

def init():
    """初始化Chroma持久化客户端和Collection"""
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
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
    """写入或更新文本块、元数据和向量"""

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

def search_chunks(query_embedding:list[float], knowledge_base_id: int, n_results: int):
    """接收用户问题转换得到的查询向量，返回文本块、来源元数据和相似度距离"""

    client, collection = init()
    query_result = collection.query(
        # collection.query() 接收的是二维向量列表，所以单条查询向量需要包装成列表。
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"knowledge_base_id":knowledge_base_id},
        include=["documents", "metadatas", "distances"]
    )
    # 输出包含多个字段的字典dict
    return query_result


