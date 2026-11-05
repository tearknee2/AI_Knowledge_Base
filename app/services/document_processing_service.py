# document_processing_service

from app.repositories.document_repository import DocumentRepository
from app.rag.txt_loader import load_txt
from app.rag.chunk_size_overlap import build_chunks
from app.rag.embedding import embed_texts
from app.rag.vector_store import init, upsert_chunks, delete_document_chunks
from uuid import uuid4

class DocumentProcessingService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    def query_document(self, document_id: int):
        # 负责查询文档
        result =self.repository.get_by_id(document_id)

        if result is None:
            raise ValueError("文档不存在")

        return result

    def load_and_split_document(self, document):
        # 负责加载和切分
        # 文件读取和清洗
        load_clean_result = load_txt(document.file_path)
        # 文本分块
        split_result = build_chunks(load_clean_result)
        # 返回文本块
        return split_result

    def vectorize_document(self, texts):
        """得到文本块并生成向量"""
        vectors = embed_texts(texts)
        return vectors

    def store_document_vectors(self, document_id: int):
        # 负责组织完整流程、写入向量、校验版本及更新状态
        # 1.查询文档
        document = self.query_document(document_id)

        try:
            self.repository.update_status(
                document_id,
                "PARSING"
            )
            # 2.读取文档并切分
            self.repository.update_status(
                document_id,
                "CHUNKING"
            )
            chunks = self.load_and_split_document(document)
            # 3.生成新向量
            self.repository.update_status(
                document_id,
                "EMBEDDING"
            )
            # 3.为本次处理生成唯一版本号
            version = uuid4().hex

            for i in range(0, len(chunks), 1000):
                # 1.获取当前批次
                batch_chunks = chunks[i:i+1000]

                # 2.提取当前批次文本
                batch_texts = [chunk["text"] for chunk in batch_chunks]

                # 3.生成当前批次向量
                batch_embeddings = self.vectorize_document(batch_texts)

                # 4.生成当前批次IDS（列表推导式）
                batch_ids = [
                    f"doc_{document_id}_{version}_chunk_{j}"
                    for j in range(i, i+len(batch_chunks))
                ]

                # 5.生成当前批次Metadatas（列表推导式）
                batch_metadatas = [
                    {
                    "knowledge_base_id": document.knowledge_base_id,
                    "document_id": document.id,
                    "chunk_index": j,
                    "file_name": document.file_name,
                    "version": version,
                    "section_path": " > ".join(chunks[j]["section_path"]),
                }
                for j in range(i, i+len(batch_chunks))
                ]

                if not (
                        len(batch_ids)
                        == len(batch_texts)
                        == len(batch_metadatas)
                        == len(batch_embeddings)
                ):
                    raise RuntimeError("当前批次数据数量不一致")
                print(
                    f"当前批次起点: {i}, "
                    f"当前批次数量: {len(batch_chunks)}, "
                    f"IDs: {len(batch_ids)}, "
                    f"Texts: {len(batch_texts)}, "
                    f"Metadatas: {len(batch_metadatas)}, "
                    f"Embeddings: {len(batch_embeddings)}"
                )
                # 6.写入当前批次ChromaDB
                upsert_chunks(batch_ids, batch_texts, batch_metadatas, batch_embeddings)


            # 6.查询刚写入的新版本，验证数量
            client, collection = init()

            result = collection.get(
                where={
                    "$and":[
                        {"document_id": document_id},
                        {"version": version}
                    ]
                }
            )

            if len(result["ids"]) != len(chunks):
                raise RuntimeError("新版本向量数量校验失败")

            # 7. 新版本验证通过后，查询该文档的全部向量
            client, collection = init()

            all_vectors = collection.get(
                where={"document_id": document_id},
                include=["metadatas"],
            )

            # 8. 找出不属于当前版本的旧向量 ID
            old_ids = [
                vector_id
                for vector_id, metadata in zip(
                    all_vectors["ids"],
                    all_vectors["metadatas"],
                )
                if metadata is None or metadata.get("version") != version
            ]

            # 9. 只删除旧向量，保留当前版本
            if old_ids:
                collection.delete(ids=old_ids)


            self.repository.update_status(
                document_id,
                "COMPLETED"
            )
        except Exception as exc:
            try:
                self.repository.update_status(document_id, "FAILED", str(exc))
            except Exception:
                pass
            raise

        return len(chunks)