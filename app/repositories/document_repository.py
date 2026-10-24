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
