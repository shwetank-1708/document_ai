from fastapi import FastAPI
from app.routes.document import router as document_router

app = FastAPI(
    title="Document AI API",
    description="OCR-based Intelligent Document Processing System",
    version="1.0.0"
)

app.include_router(document_router)

@app.get("/")
def home():
    return {"message": "Document AI API is running successfully"}
