# test_document_relationship.py
from app.core.database import SessionLocal
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document
from app.models.user import User

db = SessionLocal()

kb = db.query(KnowledgeBase).first()
print("Knowledge Base:", kb)
print("knowledge Base ID:", kb.id)
print("Documents:", kb.documents)


document = db.query(Document).first()
print("Document:", document)
print("Document Knowledge Base:", document.knowledge_base)
print("Knowledge Base ID:", document.knowledge_base.id)

db.close()

