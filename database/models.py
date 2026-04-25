from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from database.db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(Text, nullable=False)
    saved_path = Column(Text, nullable=False)
    document_type = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    fields = relationship(
        "ExtractedField",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    feedback = relationship(
        "Feedback",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class ExtractedField(Base):
    __tablename__ = "extracted_fields"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    field_name = Column(Text, nullable=False)
    field_value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="fields")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    corrected_document_type = Column(Text, nullable=True)
    corrected_fields_json = Column(Text, nullable=True)
    user_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="feedback")
