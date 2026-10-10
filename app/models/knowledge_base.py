# knowledge_base.py
from sqlalchemy import Enum, Text, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class KnowledgeBase(Base):

    __tablename__ = 'knowledge_bases'

    user = relationship(
        "User",
        back_populates="knowledge_bases"
    )

    conversations = relationship(
        "Conversation",
        back_populates="knowledge_base"
    )

    documents = relationship(
        "Document",
        back_populates="knowledge_base"
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False
    )

    name = Column(
        String(20),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        Enum('ACTIVE', 'DISABLED'),
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