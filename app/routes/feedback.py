from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from database.crud import (
    create_feedback,
    feedback_to_dict,
    get_all_feedback,
    get_document,
    get_feedback_by_document,
)
from database.db import get_db


router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    document_id: int
    corrected_document_type: Optional[str] = None
    corrected_fields: dict = Field(default_factory=dict)
    user_notes: Optional[str] = None


@router.post("")
async def save_feedback(
    feedback: FeedbackRequest,
    db: Session = Depends(get_db),
):
    document = get_document(db, feedback.document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        saved_feedback = create_feedback(
            db,
            document_id=feedback.document_id,
            corrected_document_type=feedback.corrected_document_type,
            corrected_fields=feedback.corrected_fields,
            user_notes=feedback.user_notes,
        )
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Feedback save failed: {e}",
        ) from e

    return {
        "message": "Feedback saved successfully",
        "feedback_id": saved_feedback.id,
    }


@router.get("")
async def list_feedback(db: Session = Depends(get_db)):
    feedback_records = get_all_feedback(db)
    return [feedback_to_dict(feedback) for feedback in feedback_records]


@router.get("/{document_id}")
async def read_feedback_for_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    feedback_records = get_feedback_by_document(db, document_id)
    return [feedback_to_dict(feedback) for feedback in feedback_records]
