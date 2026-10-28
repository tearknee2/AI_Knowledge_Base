from app.repositories.conversation_repository import ConversationRepository
from app.core.database import SessionLocal

db=SessionLocal()
repository = ConversationRepository(db)
conversation = repository.get_by_id(1)
print(conversation)
print(type(conversation))
fake = repository.get_by_id(9999)
print(fake)
print(type(fake))