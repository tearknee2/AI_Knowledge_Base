from app.core.database import SessionLocal
from app.services.knowledge_base_service import KnowledgeBaseService
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository

db = SessionLocal()

repo = KnowledgeBaseRepository(db)
service = KnowledgeBaseService(repo)

try:
    result1 = service.create_knowledge_base(
        {
            "user_id":1,
            "name":"数学",
            "description":"数学是世界上最伟大的学科",
            "status":"ACTIVE"
        }
    )

    print("用户1创建成功：", result1.id, result1.name)

    result2 = service.create_knowledge_base(
        {
            "user_id":2,
            "name": "数学",
            "description": "数学是世界上最伟大的学科",
            "status": "ACTIVE"
        }
    )
    print("用户2创建成功：", result2.id, result2.name)

except Exception as e:
    print(type(e).__name__, e)

finally:
    db.close()
