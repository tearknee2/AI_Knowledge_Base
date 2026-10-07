from sqlalchemy.orm import Session

class DocumentRepository:
    def __init__(self, db: Session):
        self.db = db

    # def create(self, document: Document):
