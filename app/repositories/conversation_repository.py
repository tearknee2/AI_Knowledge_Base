# conversation_repisitory
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Conversation


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id :int,
        knowledge_base_id: int,
        title: str
    ):


        conversation = Conversation(
            user_id=user_id,
            knowledge_base_id=knowledge_base_id,
            title=title
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: int):
        statement = select(Conversation).where(
            Conversation.id == conversation_id
        )
        return self.db.scalars(statement).one_or_none()