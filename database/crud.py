import json
from typing import Any, Optional

from sqlalchemy.orm import Session, selectinload

from database.models import Document, ExtractedField, Feedback


def encode_field_value(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)


def decode_field_value(value: Optional[str]) -> Any:
    if value is None:
        return None

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return value


def fields_to_dict(document: Document) -> dict:
    return {
        field.field_name: decode_field_value(field.field_value)
        for field in document.fields
    }


def document_to_dict(document: Document, include_text: bool = True) -> dict:
    data = {
        "document_id": document.id,
        "filename": document.filename,
        "saved_path": document.saved_path,
        "document_type": document.document_type,
        "confidence": document.confidence,
        "extracted_fields": fields_to_dict(document),
        "created_at": document.created_at.isoformat(),
    }

    if include_text:
        data["extracted_text"] = document.extracted_text

    return data


def create_document(
    db: Session,
    *,
    filename: str,
    saved_path: str,
    document_type: str,
    confidence: float,
    extracted_text: str,
    extracted_fields: dict,
) -> Document:
    document = Document(
        filename=filename,
        saved_path=saved_path,
        document_type=document_type,
        confidence=confidence,
        extracted_text=extracted_text,
    )

    for field_name, field_value in extracted_fields.items():
        document.fields.append(
            ExtractedField(
                field_name=field_name,
                field_value=encode_field_value(field_value),
            )
        )

    db.add(document)
    db.commit()
    db.refresh(document)
    return get_document(db, document.id) or document


def get_documents(db: Session) -> list[Document]:
    return (
        db.query(Document)
        .options(selectinload(Document.fields))
        .order_by(Document.created_at.desc())
        .all()
    )


def get_document(db: Session, document_id: int) -> Optional[Document]:
    return (
        db.query(Document)
        .options(selectinload(Document.fields))
        .filter(Document.id == document_id)
        .first()
    )


def feedback_to_dict(feedback: Feedback) -> dict:
    return {
        "feedback_id": feedback.id,
        "document_id": feedback.document_id,
        "corrected_document_type": feedback.corrected_document_type,
        "corrected_fields": decode_field_value(feedback.corrected_fields_json) or {},
        "user_notes": feedback.user_notes,
        "created_at": feedback.created_at.isoformat(),
    }


def create_feedback(
    db: Session,
    *,
    document_id: int,
    corrected_document_type: Optional[str],
    corrected_fields: dict,
    user_notes: Optional[str],
) -> Feedback:
    feedback = Feedback(
        document_id=document_id,
        corrected_document_type=corrected_document_type,
        corrected_fields_json=json.dumps(corrected_fields or {}),
        user_notes=user_notes,
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_all_feedback(db: Session) -> list[Feedback]:
    return db.query(Feedback).order_by(Feedback.created_at.desc()).all()


def get_feedback_by_document(db: Session, document_id: int) -> list[Feedback]:
    return (
        db.query(Feedback)
        .filter(Feedback.document_id == document_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )
