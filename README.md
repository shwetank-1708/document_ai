# Document AI System

An OCR-based Intelligent Document Processing System built with FastAPI and PaddleOCR.

## 🎯 Features

- **PDF/Image Upload**: Support for PNG, JPG, JPEG, WEBP, and PDF files
- **Intelligent OCR**: Uses PaddleOCR for accurate text extraction
- **Multi-page PDF Support**: Automatically converts PDF pages to images for processing
- **Document Classification**: TF-IDF based classifier to identify document types (Invoice, Resume, Form)
- **REST API**: FastAPI-based endpoint for easy integration
- **Swagger UI**: Built-in interactive API documentation

## 🛠️ Tech Stack

- **Backend Framework**: FastAPI
- **OCR Engine**: PaddleOCR
- **PDF Processing**: PyMuPDF
- **ML Classification**: Scikit-learn (TF-IDF + Logistic Regression)
- **Image Processing**: PIL, NumPy, OpenCV
- **API Server**: Uvicorn

## 📋 Project Structure

```
document_ai/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── routes/
│   │   └── document.py         # Document upload & processing routes
│   ├── services/
│   │   ├── ocr_service.py      # OCR extraction logic
│   │   └── classifier_service.py # Document classification
│   ├── core/
│   │   └── utils.py            # Utility functions
│   └── models/                 # Trained models (auto-generated)
├── data/
│   └── uploads/                # Uploaded documents (auto-created)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/shwetank-1708/document_ai.git
cd document_ai
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Server

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### Testing with Swagger UI

1. Open: `http://127.0.0.1:8000/docs`
2. Click on **POST /documents/upload**
3. Upload a document (PNG, JPG, PDF, etc.)
4. Check the response with extracted text and document type

## 📝 API Endpoints

### POST /documents/upload

Upload a document and extract text with classification.

**Request:**
- File: Binary image or PDF file

**Response:**
```json
{
  "filename": "invoice.pdf",
  "saved_as": "c3d9f8f402d54f5b8c1f3e4e8f90abcd.pdf",
  "file_path": "data/uploads/c3d9f8f402d54f5b8c1f3e4e8f90abcd.pdf",
  "extracted_text": "INVOICE\nInvoice No: INV-2026-0422\n...",
  "document_type": "invoice"
}
```

## 🔧 Configuration

No configuration needed for basic usage. The system auto-creates:
- `data/uploads/` - Uploaded files directory
- `app/models/` - Trained ML models

## 📚 Current Phase

**Phase 1: OCR Pipeline** ✅
- FastAPI setup
- File upload endpoint
- OCR text extraction (PaddleOCR)
- Basic document classification
- API response with extracted text

**Upcoming:**
- Phase 2: Enhanced preprocessing and better classifier
- Phase 3: Field extraction (invoice numbers, dates, amounts)
- Phase 4: Database integration
- Phase 5: Web UI dashboard

## 🤝 Contributing

This is a learning/development project. Feel free to extend it!

Potential improvements:
- Improve training dataset for classification
- Add field extraction logic
- Implement database storage
- Add web interface
- Performance optimization
- Error handling improvements

## 📄 License

MIT

## 👤 Author

Shwetank Chauhan

## 📧 Contact

For questions or suggestions, reach out via GitHub issues.

---

**Last Updated**: April 23, 2026
**Status**: Active Development (Phase 1 Complete)
