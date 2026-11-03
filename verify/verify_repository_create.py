from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.core.database import SessionLocal


db = SessionLocal()

repository = KnowledgeBaseRepository(db)
result = repository.create(
        {
            "user_id":1,
            "name":"repository_test",
            "description":"test repository",
            "status":"ACTIVE"
        }
    )
print(result.id)
print(result.user_id)
print(result.name)
print(result.description)
print(result.status)

db.close()

