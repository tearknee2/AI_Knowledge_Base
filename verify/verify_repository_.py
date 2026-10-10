# verify_repository.py
from app.core.database import SessionLocal
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.models import KnowledgeBase

db = SessionLocal()

repository = KnowledgeBaseRepository(db)

result = repository.get_by_id(1)

if result:
    print(result)
    print(result.id)
    print(result.name)
else:
    print("没有找到知识库")

db.close()