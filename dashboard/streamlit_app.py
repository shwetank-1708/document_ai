import json
import os
from typing import Any

import requests
import streamlit as st


DEFAULT_API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="Document AI Dashboard",
    layout="wide",
)


API_BASE_URL = st.sidebar.text_input("FastAPI URL", DEFAULT_API_BASE_URL).rstrip("/")


def api_get(path: str) -> Any:
    response = requests.get(f"{API_BASE_URL}{path}", timeout=20)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict) -> Any:
    response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=20)
    response.raise_for_status()
    return response.json()


def load_documents() -> list[dict]:
    try:
        return api_get("/documents")
    except requests.RequestException as exc:
        st.error(f"Could not load documents: {exc}")
        return []


def load_document(document_id: int) -> dict | None:
    try:
        return api_get(f"/documents/{document_id}")
    except requests.RequestException as exc:
        st.error(f"Could not load document {document_id}: {exc}")
        return None


def parse_corrected_fields(raw_json: str) -> dict | None:
    if not raw_json.strip():
        return {}

    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as exc:
        st.error(f"Corrected fields must be valid JSON: {exc}")
        return None

    if not isinstance(parsed, dict):
        st.error("Corrected fields must be a JSON object.")
        return None

    return parsed


def submit_feedback(document_id: int, corrected_document_type: str, corrected_fields: dict, user_notes: str) -> None:
    payload = {
        "document_id": document_id,
        "corrected_document_type": corrected_document_type or None,
        "corrected_fields": corrected_fields,
        "user_notes": user_notes or None,
    }

    try:
        result = api_post("/feedback", payload)
    except requests.RequestException as exc:
        st.error(f"Could not submit feedback: {exc}")
        return

    st.success(result.get("message", "Feedback saved successfully"))


st.title("Document AI Dashboard")

documents = load_documents()

if not documents:
    st.info("No processed documents found yet. Process a document from the FastAPI docs, then refresh this dashboard.")
    st.stop()

table_rows = [
    {
        "document_id": document["document_id"],
        "filename": document["filename"],
        "document_type": document["document_type"],
        "confidence": document["confidence"],
        "created_at": document.get("created_at"),
    }
    for document in documents
]

st.subheader("Processed Documents")
st.dataframe(table_rows, use_container_width=True, hide_index=True)

document_ids = [document["document_id"] for document in documents]
selected_document_id = st.selectbox(
    "Select document",
    document_ids,
    format_func=lambda document_id: f"Document {document_id}",
)

document = load_document(selected_document_id)
if document is None:
    st.stop()

left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("Document Details")
    st.text_input("Filename", document["filename"], disabled=True)
    st.text_input("Document type", document["document_type"], disabled=True)
    st.metric("Confidence", f"{document['confidence']:.3f}")

    st.subheader("Extracted Fields")
    st.json(document.get("extracted_fields", {}))

with right_col:
    st.subheader("Extracted Text")
    st.text_area(
        "OCR text",
        document.get("extracted_text") or "",
        height=360,
        disabled=True,
        label_visibility="collapsed",
    )

st.divider()
st.subheader("Submit Feedback")

with st.form("feedback_form"):
    corrected_document_type = st.text_input(
        "Corrected document type",
        value=document.get("document_type") or "",
        placeholder="invoice, resume, or form",
    )
    corrected_fields_raw = st.text_area(
        "Corrected fields JSON",
        value=json.dumps(document.get("extracted_fields", {}), indent=2),
        height=220,
    )
    user_notes = st.text_area(
        "User notes",
        placeholder="Describe what was corrected.",
        height=120,
    )
    submitted = st.form_submit_button("Submit feedback")

if submitted:
    corrected_fields = parse_corrected_fields(corrected_fields_raw)
    if corrected_fields is not None:
        submit_feedback(
            selected_document_id,
            corrected_document_type.strip(),
            corrected_fields,
            user_notes.strip(),
        )
