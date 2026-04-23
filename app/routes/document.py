from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.utils import UPLOAD_DIR, generate_unique_filename
from app.services.ocr_service import extract_text
from app.services.classifier_service import classify_document

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/upload")
async def upload_and_extract(file: UploadFile = File(...)):
    allowed_extensions = [".png", ".jpg", ".jpeg", ".webp", ".pdf"]
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PNG, JPG, JPEG, WEBP, or PDF."
        )
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_filename
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        extracted_text = extract_text(str(file_path))
        document_type = classify_document(extracted_text)
        return {
            "filename": file.filename,
            "saved_as": unique_filename,
            "file_path": str(file_path),
            "extracted_text": extracted_text,
            "document_type": document_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
