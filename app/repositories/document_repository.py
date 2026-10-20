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
