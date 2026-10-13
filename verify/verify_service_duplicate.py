# verify_service_duplicate.py
from app.core.database import SessionLocal
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.services.knowledge_base_service import KnowledgeBaseService

db = SessionLocal()

repository = KnowledgeBaseRepository(db)

service = KnowledgeBaseService(repository)
try:
    result1 = service.create_knowledge_base(
        {
            "user_id": 1,
            "name":"duplicate_test",
            "description":"test",
            "status":"ACTIVE"
        }
    )
    print(result1.id)
    print(result1.name)

    result2 = service.create_knowledge_base(
        {
            "user_id": 1,
            "name":"duplicate_test",
            "description":"test",
            "status":"ACTIVE"
        }
    )
    print(result2.id)
    print(result2.name)
except Exception as e:
    print(e)