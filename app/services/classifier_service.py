import re
import csv
import joblib
from pathlib import Path
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

MODEL_DIR = Path("app/models")
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"
CLASSIFIER_PATH = MODEL_DIR / "document_classifier.pkl"
DATASET_PATH = Path("data/ocr_dataset.csv")
RANDOM_STATE = 42

# Text preprocessing function
def preprocess_text(text: str) -> str:
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation and numbers
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

invoice_texts = [
    "invoice number 12345 date march 15 2023 total amount 250000 customer john doe",
    "bill of sale invoice 67890 payment due april 30 2023 amount due 150000",
    "tax invoice gst number 123456789 total 50000 including tax",
    "commercial invoice exporter abc company importer xyz corp value 100000",
    "service invoice for consulting services total fee 75000 due date may 1 2023",
    "purchase invoice supplier tech solutions amount 200000 terms net 30",
    "freight invoice shipping charges 25000 destination new york",
    "utility invoice electricity bill for march 2023 total 12000",
    "medical invoice patient bill total charges 85000 insurance covered 60000",
    "hotel invoice guest name jane smith total stay 45000"
]

resume_texts = [
    "john doe software engineer 5 years experience python java javascript",
    "mary smith marketing manager digital marketing seo social media experience",
    "david johnson data scientist machine learning python r statistics phd",
    "sarah wilson project manager agile scrum certification 8 years experience",
    "michael brown sales representative b2b sales crm software experience",
    "lisa davis graphic designer adobe creative suite portfolio website design",
    "robert miller financial analyst excel financial modeling cpa certification",
    "jennifer garcia teacher education masters degree classroom experience",
    "kevin lee chef culinary arts fine dining restaurant management",
    "amy white nurse registered nurse bsn healthcare experience"
]

form_texts = [
    "application form personal information name address phone email",
    "contact form message subject inquiry customer service request",
    "registration form event details participant information payment method",
    "survey form feedback questions rating scale comments section",
    "order form product selection quantity shipping address billing info",
    "membership form application details benefits membership fee",
    "complaint form issue description date location contact information",
    "feedback form satisfaction rating suggestions improvement ideas",
    "subscription form newsletter preferences email frequency content topics",
    "enrollment form course selection student details payment information"
]

TRAINING_DATA = {
    "invoice": invoice_texts,
    "resume": resume_texts,
    "form": form_texts,
}


def load_ocr_dataset() -> Tuple[List[str], List[str]]:
    texts = []
    labels = []

    if not DATASET_PATH.exists():
        return texts, labels

    with DATASET_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            text = (row.get("text") or "").strip()
            label = (row.get("label") or "").strip()
            if text and label:
                texts.append(text)
                labels.append(label)

    return texts, labels


def get_dataset_summary() -> dict:
    _, labels = load_ocr_dataset()
    if labels:
        return {
            document_type: labels.count(document_type)
            for document_type in sorted(set(labels))
        }

    return {
        document_type: len(samples)
        for document_type, samples in TRAINING_DATA.items()
    }


def get_training_examples() -> Tuple[List[str], List[str]]:
    dataset_texts, dataset_labels = load_ocr_dataset()
    if dataset_texts:
        return dataset_texts, dataset_labels

    texts = []
    labels = []

    for document_type, samples in TRAINING_DATA.items():
        texts.extend(samples)
        labels.extend([document_type] * len(samples))

    return texts, labels


def evaluate_model(texts, labels, model, vectorizer) -> Tuple[float, dict]:
    processed_texts = [preprocess_text(text) for text in texts]
    X = vectorizer.transform(processed_texts)
    y_pred = model.predict(X)

    accuracy = accuracy_score(labels, y_pred)
    report = classification_report(
        labels,
        y_pred,
        output_dict=True,
        zero_division=0,
    )

    return accuracy, report


def train_classifier() -> dict:
    X, y = get_training_examples()
    X_processed = [preprocess_text(text) for text in X]

    X_train, X_test, y_train, y_test = train_test_split(
        X_processed,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)

    classifier = LogisticRegression(random_state=RANDOM_STATE, max_iter=1000)
    classifier.fit(X_train_vectorized, y_train)

    y_pred = classifier.predict(X_test_vectorized)
    accuracy, report = evaluate_model(X_test, y_test, classifier, vectorizer)
    labels_order = sorted(set(y))

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    joblib.dump(classifier, CLASSIFIER_PATH)

    return {
        "dataset_size_per_class": get_dataset_summary(),
        "total_samples": len(X),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "accuracy": round(accuracy, 3),
        "classification_report": report,
        "classification_report_text": classification_report(
            y_test,
            y_pred,
            labels=labels_order,
            zero_division=0,
        ),
        "confusion_matrix": {
            "labels": labels_order,
            "matrix": confusion_matrix(y_test, y_pred, labels=labels_order).tolist(),
        },
    }


def ensure_model_files() -> None:
    if not VECTORIZER_PATH.exists() or not CLASSIFIER_PATH.exists():
        train_classifier()


def evaluate_classifier() -> dict:
    return train_classifier()


def load_classifier() -> Tuple[TfidfVectorizer, LogisticRegression]:
    ensure_model_files()
    vectorizer = joblib.load(VECTORIZER_PATH)
    classifier = joblib.load(CLASSIFIER_PATH)
    return vectorizer, classifier


def predict_with_confidence(text: str, model, vectorizer) -> Tuple[str, float]:
    # Preprocess input text
    processed_text = preprocess_text(text)

    # Vectorize
    text_vectorized = vectorizer.transform([processed_text])

    probabilities = model.predict_proba(text_vectorized)[0]
    prediction = model.classes_[probabilities.argmax()]
    confidence = probabilities.max()

    return str(prediction), float(confidence)


# Classification function with confidence
def classify_document(text: str) -> dict:
    vectorizer, classifier = load_classifier()
    prediction, confidence = predict_with_confidence(text, classifier, vectorizer)

    return {
        "document_type": prediction,
        "confidence": round(float(confidence), 3)
    }
