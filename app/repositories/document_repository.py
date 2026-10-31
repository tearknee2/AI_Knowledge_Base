# document_repository
from sqlalchemy.orm import Session
from app.models.document import Document

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        document_data: dict,
        ):

        document = Document(**document_data)
        self.db.add(document)
        try:
            self.db.commit()
            self.db.refresh(document)
        except Exception:
            self.db.rollback()
            raise
        return document

    def get_by_knowledge_base_id(self, knowledge_base_id: int):
        """
        根据知识库ID，查询这个知识库下的所有文档，并返回文档对象列表
        :param knowledge_base_id: 知识库id
        :return: 文档对象列表
        """
        return self.db.query(Document).filter(
            Document.knowledge_base_id == knowledge_base_id
        ).all()

    def get_by_id(self, document_id: int):
        """根据文档id返回文档对象，查不到返回None"""
        return (
            self.db.query(Document)
            .filter(Document.id == document_id)
            .first()
        )

    def update_status(
            self,
            document_id: int,
            status: str,
            error_message: str | None = None,
    ):

        document = self.get_by_id(document_id)

        if document is None:
            return None
        document.status = status
        document.error_message = error_message

        try:
            self.db.commit()
            self.db.refresh(document)
        except Exception:
            self.db.rollback()
            raise

        return document

    def get_completed_document_ids(self, knowledge_base_id: int) -> list[int] :
        """返回指定知识库中处理成功的文档 ID 列表"""
        ids = self.db.query(Document.id).filter(
            Document.knowledge_base_id == knowledge_base_id,
            Document.status == "COMPLETED",
        ).all()

        return [row[0] for row in ids]