import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.classifier_service import (
    evaluate_classifier,
    get_dataset_summary,
    load_classifier,
    predict_with_confidence,
)


UNSEEN_TEST_SAMPLES = [
    (
        "ACME Corp invoice INV-9981 billing date April 23 2026 subtotal 1199 "
        "tax 96 amount due 1295 payment terms net 15",
        "invoice",
    ),
    (
        "Priya Sharma senior backend engineer resume skills python fastapi "
        "postgresql aws seven years experience education btech",
        "resume",
    ),
    (
        "Patient intake form full name date of birth address phone insurance "
        "provider emergency contact signature consent",
        "form",
    ),
    (
        "Tax invoice from Blue River Services invoice number BRS-204 total "
        "balance due 7420 bank transfer payment due date",
        "invoice",
    ),
    (
        "Job application form applicant name current employer education history "
        "references declaration signature",
        "form",
    ),
]


def confidence_band(confidence: float) -> str:
    if confidence > 0.80:
        return "strong"
    if confidence >= 0.60:
        return "okay"
    if confidence >= 0.40:
        return "weak"
    return "unreliable"


def main() -> None:
    metrics = evaluate_classifier()

    print("Dataset size per class:")
    for document_type, count in get_dataset_summary().items():
        print(f"  {document_type}: {count}")

    print()
    print("Train/test split:")
    print(f"  Total samples: {metrics['total_samples']}")
    print(f"  Train samples: {metrics['train_samples']}")
    print(f"  Test samples: {metrics['test_samples']}")

    print()
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(metrics["classification_report_text"])

    vectorizer, classifier = load_classifier()

    print("Unseen sample confidence checks:")
    for text, true_label in UNSEEN_TEST_SAMPLES:
        prediction, confidence = predict_with_confidence(text, classifier, vectorizer)
        result = "PASS" if prediction == true_label else "FAIL"
        print(
            f"True: {true_label:7} | Pred: {prediction:7} | "
            f"Conf: {confidence:.2f} ({confidence_band(confidence)}) | {result}"
        )


if __name__ == "__main__":
    main()
