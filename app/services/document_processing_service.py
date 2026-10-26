# document_processing_service

from app.repositories.document_repository import DocumentRepository
from app.rag.txt_loader import load_txt
from app.rag.chunk_size_overlap import split_text
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
        split_result = split_text(load_clean_result, 500, 50)
        # 返回文本块
        return split_result

    def vectorize_document(self, chunks):
        """得到文本块并生成向量"""
        vectors = embed_texts(chunks)
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
            embeddings = self.vectorize_document(chunks)

            # 3.为本次处理生成唯一版本号
            version = uuid4().hex

            # 4.生成带版本号的文本块id
            ids = [
                f"doc_{document_id}_{version}_chunk_{i}"
                for i in range(len(chunks))
            ]

            # 4.为每个文本块准备来源元数据
            metadatas = [
                {
                    "knowledge_base_id": document.knowledge_base_id,
                    "document_id": document.id,
                    "chunk_index": i,
                    "file_name": document.file_name,
                    "version": version
                }
                for i in range(len(chunks))
            ]

            # 5.先写入新版本向量
            upsert_chunks(ids, chunks, metadatas, embeddings)

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