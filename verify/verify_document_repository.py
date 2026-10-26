from app.repositories.document_repository import DocumentRepository
from app.core.database import SessionLocal

db = SessionLocal()
try:
    document_repository = DocumentRepository(db)
    document1 = document_repository.get_by_id(1)
    print(f"存在的文档1")
    print({
        "id": document1.id,
        "file_name": document1.file_name,
        "status": document1.status,
    })

    document999 = document_repository.get_by_id(999)
    print(f"不存在的文档{document999}")

    document_repository.update_status(2, 'COMPLETED')
    finished_document = document_repository.get_by_id(2)
    print("更新后的状态")
    print(finished_document.status)
finally:
    db.close()