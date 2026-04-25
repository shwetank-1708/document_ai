import logging
import time
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.utils import UPLOAD_DIR, generate_unique_filename
from app.services.ocr_service import extract_text
from app.services.classifier_service import classify_document
from app.services.extraction_service import extract_fields
from database.crud import (
    create_document,
    document_to_dict,
    get_document,
    get_documents,
)
from database.db import get_db

router = APIRouter(prefix="/documents", tags=["Documents"])
process_router = APIRouter(tags=["Documents"])
logger = logging.getLogger(__name__)
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
LOW_CONFIDENCE_THRESHOLD = 0.60


async def process_uploaded_file(file: UploadFile, db: Session) -> dict:
    start_time = time.perf_counter()
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        logger.warning("Rejected unsupported file type: filename=%s", file.filename)
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PNG, JPG, JPEG, WEBP, or PDF."
        )

    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_filename

    try:
        logger.info("Upload started: filename=%s saved_as=%s", file.filename, unique_filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        logger.info("Upload saved: path=%s size_bytes=%s", file_path, len(content))

        logger.info("OCR started: path=%s", file_path)
        extracted_text = extract_text(str(file_path))
        if not extracted_text.strip():
            logger.warning("OCR returned empty output: filename=%s path=%s", file.filename, file_path)
            raise HTTPException(
                status_code=422,
                detail="OCR could not extract text from the uploaded document.",
            )
        logger.info("OCR completed: chars=%s", len(extracted_text))

        logger.info("Classification started: filename=%s", file.filename)
        classification = classify_document(extracted_text)
        logger.info(
            "Classification completed: document_type=%s confidence=%.3f",
            classification["document_type"],
            classification["confidence"],
        )

        logger.info("Extraction started: document_type=%s", classification["document_type"])
        extracted_fields = extract_fields(
            classification["document_type"],
            extracted_text,
        )
        logger.info("Extraction completed: field_count=%s", len(extracted_fields))

        try:
            logger.info("Database save started: filename=%s", file.filename)
            document = create_document(
                db,
                filename=file.filename,
                saved_path=str(file_path),
                document_type=classification["document_type"],
                confidence=classification["confidence"],
                extracted_text=extracted_text,
                extracted_fields=extracted_fields,
            )
            logger.info("Database save completed: document_id=%s", document.id)
        except SQLAlchemyError as e:
            db.rollback()
            logger.exception("Database save failed: filename=%s", file.filename)
            raise HTTPException(
                status_code=500,
                detail="Database save failed. Please try again.",
            ) from e

        processing_seconds = time.perf_counter() - start_time
        logger.info(
            "Document processed: document_id=%s filename=%s processing_time=%.2fs",
            document.id,
            file.filename,
            processing_seconds,
        )

        response = {
            "document_id": document.id,
            "filename": file.filename,
            "saved_as": unique_filename,
            "file_path": str(file_path),
            "document_type": classification["document_type"],
            "confidence": classification["confidence"],
            "extracted_fields": extracted_fields,
            "extracted_text": extracted_text,
            "processing_time": f"{processing_seconds:.2f} seconds",
        }

        if classification["confidence"] < LOW_CONFIDENCE_THRESHOLD:
            response["warning"] = "Low confidence prediction"

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Document processing failed: filename=%s", file.filename)
        raise HTTPException(
            status_code=500,
            detail="Document processing failed. Please try again.",
        ) from e


def format_process_response(result: dict) -> dict:
    response = {
        "document_id": result["document_id"],
        "filename": result["filename"],
        "document_type": result["document_type"],
        "confidence": result["confidence"],
        "extracted_fields": result["extracted_fields"],
        "extracted_text": result["extracted_text"],
        "processing_time": result["processing_time"],
    }

    if "warning" in result:
        response["warning"] = result["warning"]

    return response


@router.post("/upload")
async def upload_and_extract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return await process_uploaded_file(file, db)


@router.get("")
async def list_documents(db: Session = Depends(get_db)):
    documents = get_documents(db)
    return [document_to_dict(document, include_text=False) for document in documents]


@router.get("/{document_id}")
async def read_document(document_id: int, db: Session = Depends(get_db)):
    document = get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return document_to_dict(document)


@process_router.post("/process-document")
async def process_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    result = await process_uploaded_file(file, db)
    return format_process_response(result)
