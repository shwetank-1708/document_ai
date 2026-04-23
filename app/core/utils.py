from pathlib import Path
import uuid

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def generate_unique_filename(filename: str) -> str:
    ext = Path(filename).suffix
    return f"{uuid.uuid4().hex}{ext}"
