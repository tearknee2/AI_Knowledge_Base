# document.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Text,
    BigInteger,
    Enum
    )

from sqlalchemy.orm import relationship

from sqlalchemy.sql import func

from app.core.database import Base

class Document(Base):

    __tablename__ = "documents"

    knowledge_base = relationship(
        "KnowledgeBase",
        back_populates="documents"
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    knowledge_base_id = Column(
        Integer,
        ForeignKey("knowledge_bases.id"),
        nullable=False
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    file_type = Column(
        String(20),
        nullable=False
    )

    file_size = Column(
        BigInteger,
        nullable=False
    )

    status = Column(
        Enum(
            "PENDING",
            "PARSING",
            "CHUNKING",
            "EMBEDDING",
            "COMPLETED",
            "FAILED"
        ),
        nullable=False
    )

    error_message = Column(
        Text,
        nullable=True
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