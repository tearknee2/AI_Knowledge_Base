from app.core.database import SessionLocal
from app.repositories.document_repository import DocumentRepository
from app.services.document_processing_service import DocumentProcessingService

db = SessionLocal()

try:
    repository = DocumentRepository(db)
    service = DocumentProcessingService(repository)

    for document_id in [4,5]:
        document = service.query_document(document_id)

        if document is None:
            print(f"文档{document_id}不存在")
            continue
        print(f"\n文档 ID：{document.id}")
        print(f"知识库 ID：{document.knowledge_base_id}")
        print(f"文件名：{document.file_name}")
        print(f"状态：{document.status}")
        print(f"错误信息：{document.error_message}")
finally:
    db.close()
