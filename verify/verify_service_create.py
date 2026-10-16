# verify_service_create.py
from AI_Knowledge_Base.app.core.database import SessionLocal
from AI_Knowledge_Base.app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from AI_Knowledge_Base.app.services.knowledge_base_service import KnowledgeBaseService

db = SessionLocal()

repository = KnowledgeBaseRepository(db)

service = KnowledgeBaseService(repository)

result = service.create_knowledge_base(
    {
        "user_id": 1,
        "name": "service_test_1016",
        "description": "test service"
    }
)
print(result.id)
print(result.name)
print(result.description)
print(result.status)

db.close()