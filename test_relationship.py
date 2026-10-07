from app.core.database import SessionLocal
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase

db = SessionLocal()

user = db.query(User).first()

print("User:", user)
print("User ID:", user.id)
print("User Name:", user.knowledge_bases)


kb = db.query(KnowledgeBase).first()

print("Knowledge Base:", kb)
print("Knowledge Base User:", kb.user)
print("User ID:", kb.user.id)

db.close()
