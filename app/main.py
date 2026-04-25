from fastapi import FastAPI
from app.routes.document import process_router, router as document_router
from app.routes.feedback import router as feedback_router
from database.db import init_db
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)

app = FastAPI(
    title="Document AI API",
    description="OCR-based Intelligent Document Processing System",
    version="1.0.0"
)

init_db()

app.include_router(document_router)
app.include_router(process_router)
app.include_router(feedback_router)

@app.get("/")
def home():
    return {"message": "Document AI API is running successfully"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
