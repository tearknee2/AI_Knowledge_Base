# document_service
import shutil
import uuid

from pathlib import Path
from fastapi import UploadFile
from app.services.knowledge_base_service import KnowledgeBaseService
from app.repositories.document_repository import DocumentRepository
from app.services.document_processing_service import DocumentProcessingService



class DocumentService:
    def __init__(
        self,
        repository: DocumentRepository,
        knowledge_base_service: KnowledgeBaseService,
        document_processing_service: DocumentProcessingService
):
        self.repository = repository
        self.knowledge_base_service = knowledge_base_service
        self.document_processing_service = document_processing_service

    def upload_document(
        self,
        knowledge_base_id: int,
        file: UploadFile,
        user_id: int
    ):
        self.knowledge_base_service.get_knowledge_base_by_id(
            knowledge_base_id,
            user_id=user_id
        )

        # base_dir = Path(__file__).resolve().parent.parent
        base_dir = Path(__file__).resolve().parents[2]
        upload_dir = base_dir / "uploads" / str(knowledge_base_id)
        Path(upload_dir).mkdir(parents=True,exist_ok=True)

        suffix = Path(file.filename).suffix
        file_type = suffix.lstrip(".")
        unique_name = uuid.uuid4().hex + suffix
        save_path = upload_dir / unique_name


        with open(save_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        file_size = save_path.stat().st_size

        document_data = {
            "knowledge_base_id": knowledge_base_id,
            "file_name": file.filename,
            "file_path": str(save_path),
            "file_type": file_type,
            "file_size": file_size,
            "status": "PENDING",
        }

        try:
            result = self.repository.create(document_data)
        except Exception:
            Path(save_path).unlink(missing_ok=True)
            raise
        self.document_processing_service.store_document_vectors(result.id)

        return result

    def list_documents(self, knowledge_base_id: int, user_id: int):
        # 1.校验知识库是否存在，以及用户是否有权访问
        self.knowledge_base_service.get_knowledge_base_by_id(
            knowledge_base_id,
            user_id
        )

        # 2.查询该知识库下的所有文档
        result = self.repository.get_by_knowledge_base_id(knowledge_base_id)

        # 3.返回文档列表
        return result