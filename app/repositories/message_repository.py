# message_repository

from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import Message
from enum import Enum


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        conversation_id: int,
        role: str,
        content: str
    ):
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_conversation_id(self, conversation_id: int):
        statement = (select(Message)
        .where(
            Message.conversation_id == conversation_id
        ).order_by(
            Message.created_at.asc(),
            Message.id.asc()
        ))
        # 返回一个Python列表
        return self.db.scalars(statement).all()