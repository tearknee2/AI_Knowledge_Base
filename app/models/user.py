# user.py
from sqlalchemy import Column,Integer,String,DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class User(Base):

    __tablename__ = 'users'

    knowledge_bases = relationship(
        "KnowledgeBase",
        back_populates="user"
    )

    conversations = relationship(
        "Conversation",
        back_populates="user"
    )
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    username = Column(
        String(50),
        unique=True,
        nullable=False
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )