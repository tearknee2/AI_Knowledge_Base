# document_service
import shutil
import uuid

from pathlib import Path
from fastapi import UploadFile
from app.services.knowledge_base_service import KnowledgeBaseService
from app.repositories.document_repository import DocumentRepository



class DocumentService:
    def __init__(self, repository: DocumentRepository, knowledge_base_service: KnowledgeBaseService):
        self.repository = repository
        self.knowledge_base_service = knowledge_base_service

    def upload_document(self, knowledge_base_id: int, file: UploadFile):
        self.knowledge_base_service.get_knowledge_base_by_id(knowledge_base_id, user_id=1)

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
            return result
        except Exception:
            Path(save_path).unlink(missing_ok=True)
            raise