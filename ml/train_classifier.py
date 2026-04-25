import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.classifier_service import train_classifier


def main() -> None:
    metrics = train_classifier()

    print("Dataset size per class:")
    for document_type, count in metrics["dataset_size_per_class"].items():
        print(f"  {document_type}: {count}")

    print()
    print(f"Total samples: {metrics['total_samples']}")
    print(f"Train samples: {metrics['train_samples']}")
    print(f"Test samples: {metrics['test_samples']}")

    print()
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(metrics["classification_report_text"])

    print("Confusion matrix:")
    print(json.dumps(metrics["confusion_matrix"], indent=2))
    print()
    print("Classifier saved successfully")


if __name__ == "__main__":
    main()
