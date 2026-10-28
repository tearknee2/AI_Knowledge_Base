from app.core.database import SessionLocal
from app.repositories.message_repository import MessageRepository
from app.models.message import Message

db = SessionLocal()
try:
    repository = MessageRepository(db)

    repository.create(
        1,
        "user",
        "你好，你是谁啊"
    )
    repository.create(
        1,
        "assistant",
        "你好，我是deepseek大肥鱼"
    )

    messages = repository.get_by_conversation_id(1)
    print(messages)
    print(isinstance(messages, list))

    for message in messages:
        print(isinstance(message, Message))
        print(message.conversation_id,message.created_at,message.id,message.role,message.content)
        # print(message.role)
        # print(message.content)
finally:
    db.close()