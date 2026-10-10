# conversation.py
from app.core.database import Base
from sqlalchemy import Column,Integer,ForeignKey,String,DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Conversation(Base):

    __tablename__ = "conversations"

    user = relationship(
        'User',
        back_populates='conversations'
    )

    knowledge_base = relationship(
        "KnowledgeBase",
        back_populates='conversations'
    )

    messages = relationship(
       "Message",
       back_populates='conversation'
    )

    id= Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False
    )

    knowledge_base_id = Column(
        Integer,
        ForeignKey('knowledge_bases.id'),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )