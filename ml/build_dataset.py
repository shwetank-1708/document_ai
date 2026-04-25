import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.ocr_service import extract_text


TRAINING_DIR = PROJECT_ROOT / "data" / "training"
DATASET_PATH = PROJECT_ROOT / "data" / "ocr_dataset.csv"
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".pdf"}


def iter_training_files():
    for label_dir in sorted(TRAINING_DIR.iterdir()):
        if not label_dir.is_dir():
            continue

        for file_path in sorted(label_dir.iterdir()):
            if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                yield label_dir.name, file_path


def main() -> None:
    rows = []

    for label, file_path in iter_training_files():
        print(f"OCR: {label}/{file_path.name}", flush=True)
        text = extract_text(str(file_path))
        rows.append(
            {
                "file_path": str(file_path.relative_to(PROJECT_ROOT)),
                "label": label,
                "text": text,
            }
        )

    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATASET_PATH.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["file_path", "label", "text"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Total samples: {len(rows)}")
    print(f"Dataset saved successfully: {DATASET_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
