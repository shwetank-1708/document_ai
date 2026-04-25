# Document AI System

Document AI is an OCR-based intelligent document processing system for invoices, resumes, and forms. It accepts PDF/image uploads, extracts text with PaddleOCR, classifies the document, extracts key fields, stores the result in SQLite, and provides a Streamlit dashboard for review and feedback.

## Project Overview

This project demonstrates an end-to-end document AI workflow:

- Upload PDF/image documents through FastAPI
- Extract text using PaddleOCR
- Classify document type with TF-IDF + Logistic Regression
- Extract useful fields with rule-based logic
- Store processed documents and extracted fields in SQLite
- Capture user feedback for future retraining
- Review documents and submit corrections from a Streamlit dashboard

## Architecture

```text
Upload
  -> OCR
  -> Classification
  -> Field Extraction
  -> SQLite Database
  -> FastAPI Response
  -> Streamlit Dashboard
  -> Feedback Storage
```

Core components:

- `app/services/ocr_service.py`: OCR extraction for images and PDFs
- `app/services/classifier_service.py`: document type prediction
- `app/services/extraction_service.py`: invoice/resume/form field extraction
- `database/`: SQLAlchemy models, session setup, and CRUD helpers
- `dashboard/streamlit_app.py`: review and feedback UI
- `ml/`: dataset building and classifier training scripts

## Tech Stack

- FastAPI
- Streamlit
- PaddleOCR
- PyMuPDF
- Scikit-learn
- SQLAlchemy
- SQLite
- Docker Compose

## Local Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the FastAPI API:

```bash
uvicorn app.main:app --reload
```

Run the Streamlit dashboard:

```bash
streamlit run dashboard/streamlit_app.py
```

Local URLs:

- FastAPI docs: `http://127.0.0.1:8000/docs`
- Streamlit dashboard: `http://127.0.0.1:8501`

## Docker Usage

Make sure Docker is running, then start both services:

```bash
docker compose up --build
```

Docker URLs:

- FastAPI docs: `http://localhost:8000/docs`
- Streamlit dashboard: `http://localhost:8501`

Docker Compose mounts persistent local data:

- `./data/uploads:/app/data/uploads`
- `./document_ai.db:/app/document_ai.db`

Stop the containers:

```bash
docker compose down
```

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/process-document` | Upload, OCR, classify, extract fields, save to DB |
| `POST` | `/documents/upload` | Same processing flow with saved filename/path metadata |
| `GET` | `/documents` | List processed documents |
| `GET` | `/documents/{document_id}` | Get one processed document with extracted fields |
| `POST` | `/feedback` | Save corrected classification or field feedback |
| `GET` | `/feedback` | List all feedback records |
| `GET` | `/feedback/{document_id}` | List feedback for one document |

## Example Responses

### `POST /process-document`

```json
{
  "document_id": 3,
  "filename": "invoice_01.pdf",
  "document_type": "invoice",
  "confidence": 0.91,
  "extracted_fields": {
    "invoice_number": "INV-1001",
    "invoice_date": "2026-04-23",
    "total_amount": "4500",
    "vendor_name": "Acme Services"
  },
  "extracted_text": "Tax Invoice\nInvoice No: INV-1001\n...",
  "processing_time": "1.25 seconds"
}
```

When the classifier confidence is low, the response includes:

```json
{
  "warning": "Low confidence prediction"
}
```

### `GET /documents`

```json
[
  {
    "document_id": 3,
    "filename": "invoice_01.pdf",
    "saved_path": "data/uploads/abc123.pdf",
    "document_type": "invoice",
    "confidence": 0.91,
    "extracted_fields": {
      "invoice_number": "INV-1001",
      "total_amount": "4500"
    },
    "created_at": "2026-04-25T10:30:00"
  }
]
```

### `POST /feedback`

Request:

```json
{
  "document_id": 3,
  "corrected_document_type": "invoice",
  "corrected_fields": {
    "invoice_number": "INV-1001",
    "total_amount": "4500"
  },
  "user_notes": "Corrected invoice amount"
}
```

Response:

```json
{
  "message": "Feedback saved successfully",
  "feedback_id": 1
}
```

### `GET /feedback`

```json
[
  {
    "feedback_id": 1,
    "document_id": 3,
    "corrected_document_type": "invoice",
    "corrected_fields": {
      "invoice_number": "INV-1001",
      "total_amount": "4500"
    },
    "user_notes": "Corrected invoice amount",
    "created_at": "2026-04-25T10:35:00"
  }
]
```

## Training Workflow

Build the OCR dataset:

```bash
python ml/build_dataset.py
```

Retrain the classifier:

```bash
python ml/train_classifier.py
```

Keep unseen files under:

- `data/test/invoice/`
- `data/test/resume/`
- `data/test/form/`

## Reliability Features

- Per-step logging for upload, OCR, classification, extraction, and database save
- Request processing time in document processing responses
- Clear HTTP errors for unsupported files and empty OCR output
- Low-confidence warning when prediction confidence is below `0.60`
- `/health` endpoint for deployment checks

## Configuration

Default database:

```text
sqlite:///./document_ai.db
```

Override with:

```bash
DATABASE_URL=<your_database_url>
```

The Streamlit dashboard reads the API URL from:

```bash
API_BASE_URL=http://127.0.0.1:8000
```

## Status

Current phase: production polish complete.
