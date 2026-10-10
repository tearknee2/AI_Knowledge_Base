# message.py
from app.core.database import Base
from sqlalchemy import Column,Integer,ForeignKey,Enum,Text,DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Message(Base):

    __tablename__ = "messages"

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False
    )

    role = Column(
        Enum(
            'user',
            'system',
            'assistant'
        ),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )