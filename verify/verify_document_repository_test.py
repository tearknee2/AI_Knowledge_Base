from app.core.database import SessionLocal
from app.repositories.document_repository import DocumentRepository

db = SessionLocal()
try:
    document_repository = DocumentRepository(db)

    ids_list =document_repository.get_completed_document_ids(1)
    assert isinstance(ids_list, list)

    for id in ids_list:
        assert isinstance(id, int)
        result = document_repository.get_by_id(id)
        assert result.status == "COMPLETED"
finally:
    db.close()
