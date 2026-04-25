import re
from typing import Optional


EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{4,6}"
)
DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
    r"\d{4}[/-]\d{1,2}[/-]\d{1,2}|"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{1,2},?\s+\d{2,4}|"
    r"\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+\d{2,4})\b",
    re.IGNORECASE,
)
AMOUNT_PATTERN = re.compile(
    r"(?:rs\.?|inr|usd|eur|gbp|\$|₹)?\s*\d{1,3}(?:,\d{2,3})*(?:\.\d{1,2})?|\d+(?:\.\d{1,2})?"
)


COMMON_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "sql",
    "excel",
    "tableau",
    "power bi",
    "machine learning",
    "deep learning",
    "data analysis",
    "data science",
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "pytorch",
    "fastapi",
    "django",
    "flask",
    "react",
    "node",
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "git",
    "agile",
    "scrum",
    "seo",
    "crm",
    "communication",
    "leadership",
    "project management",
}


def clean_value(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    cleaned = re.sub(r"\s+", " ", value).strip(" :-|,")
    return cleaned or None


def get_lines(text: str) -> list[str]:
    return [cleaned for line in text.splitlines() if (cleaned := clean_value(line))]


def first_regex_match(text: str, patterns: list[str], group: int = 1) -> Optional[str]:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return clean_value(match.group(group))
    return None


def extract_email(text: str) -> Optional[str]:
    match = EMAIL_PATTERN.search(text)
    return clean_value(match.group(0)) if match else None


def extract_phone(text: str) -> Optional[str]:
    for match in PHONE_PATTERN.finditer(text):
        phone = clean_value(match.group(0))
        digits = re.sub(r"\D", "", phone or "")
        if 7 <= len(digits) <= 15:
            return phone
    return None


def extract_labeled_date(text: str, labels: list[str]) -> Optional[str]:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = re.compile(
        rf"(?:{label_pattern})[ \t]*(?:date)?[ \t]*[:#-]?[ \t]*({DATE_PATTERN.pattern})",
        re.IGNORECASE,
    )
    match = pattern.search(text)
    if match:
        return clean_value(match.group(1))

    match = DATE_PATTERN.search(text)
    return clean_value(match.group(0)) if match else None


def extract_invoice_number(text: str) -> Optional[str]:
    return first_regex_match(
        text,
        [
            r"\binvoice[ \t]*(?:number|no|#|id)[ \t]*[:#-][ \t]*([A-Z0-9][A-Z0-9/-]{2,})",
            r"\binv[ \t]*(?:number|no|#|id)[ \t]*[:#-][ \t]*([A-Z0-9][A-Z0-9/-]{2,})",
            r"\bbill[ \t]*(?:number|no|#)[ \t]*[:#-][ \t]*([A-Z0-9][A-Z0-9/-]{2,})",
        ],
    )


def extract_total_amount(text: str) -> Optional[str]:
    labels = [
        "grand total",
        "total amount",
        "amount due",
        "balance due",
        "invoice total",
        "net amount",
        "total",
    ]

    for label in labels:
        pattern = re.compile(
            rf"{label}[ \t]*[:#-][ \t]*({AMOUNT_PATTERN.pattern})",
            re.IGNORECASE,
        )
        matches = list(pattern.finditer(text))
        if matches:
            return clean_value(matches[-1].group(1))

    return None


def extract_vendor_name(text: str) -> Optional[str]:
    vendor = first_regex_match(
        text,
        [
            r"\b(?:vendor|seller|supplier|from)[ \t]*[:#-][ \t]*([^\n]{2,80})",
            r"\b(?:company name|business name)[ \t]*[:#-][ \t]*([^\n]{2,80})",
            r"\bfor[ \t]+([A-Za-z0-9][A-Za-z0-9 &.,'-]{2,80})",
        ],
    )
    if vendor:
        return vendor

    skip_words = {
        "invoice",
        "tax invoice",
        "bill",
        "date",
        "total",
        "amount",
        "gstin",
        "company name",
        "business name",
    }
    for line in get_lines(text)[:8]:
        lowered = line.lower()
        if any(word in lowered for word in skip_words):
            continue
        if re.search(r"[A-Za-z]", line):
            return clean_value(line)
    return None


def extract_invoice_fields(text: str) -> dict:
    return {
        "invoice_number": extract_invoice_number(text),
        "invoice_date": extract_labeled_date(text, ["invoice date", "date", "dated"]),
        "total_amount": extract_total_amount(text),
        "vendor_name": extract_vendor_name(text),
    }


def extract_candidate_name(text: str) -> Optional[str]:
    name = first_regex_match(text, [r"\b(?:candidate name|name)[ \t]*[:#-][ \t]*([A-Za-z][A-Za-z .'-]{2,80})"])
    if name:
        return name

    skip_words = {
        "resume",
        "curriculum vitae",
        "cv",
        "email",
        "phone",
        "mobile",
        "skills",
        "education",
        "experience",
        "summary",
    }
    for line in get_lines(text)[:10]:
        lowered = line.lower()
        if any(word in lowered for word in skip_words):
            continue
        if EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line):
            continue
        if re.fullmatch(r"[A-Za-z][A-Za-z .'-]{2,60}", line) and len(line.split()) <= 5:
            return clean_value(line)
    return None


def extract_skills(text: str) -> Optional[list[str]]:
    lowered = text.lower()
    found = {skill for skill in COMMON_SKILLS if re.search(rf"\b{re.escape(skill)}\b", lowered)}

    skills_line = first_regex_match(text, [r"\bskills?[ \t]*[:#-][ \t]*([^\n]{3,160})"])
    if skills_line:
        for item in re.split(r"[,;|/]", skills_line):
            item = clean_value(item)
            if item and 1 <= len(item.split()) <= 4:
                found.add(item.lower())

    if not found:
        return None

    return sorted(found)


def extract_resume_fields(text: str) -> dict:
    return {
        "candidate_name": extract_candidate_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
    }


def extract_full_name(text: str) -> Optional[str]:
    return first_regex_match(
        text,
        [
            r"\b(?:full name|applicant name|name)[ \t]*[:#-][ \t]*([A-Za-z][A-Za-z .'-]{2,80})",
            r"\bI,\s*([A-Za-z][A-Za-z .'-]{2,80}),",
        ],
    )


def extract_address(text: str) -> Optional[str]:
    return first_regex_match(
        text,
        [
            r"\b(?:address|current address|mailing address|residential address)[ \t]*[:#-][ \t]*([^\n]{5,160})",
            r"\b(?:city|state|zip|postal code)[ \t]*[:#-][ \t]*([^\n]{5,160})",
        ],
    )


def extract_form_fields(text: str) -> dict:
    return {
        "full_name": extract_full_name(text),
        "dob": extract_labeled_date(text, ["date of birth", "dob", "birth date"]),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "address": extract_address(text),
    }


def extract_fields(document_type: str, text: str) -> dict:
    document_type = (document_type or "").lower()

    if document_type == "invoice":
        return extract_invoice_fields(text)
    if document_type == "resume":
        return extract_resume_fields(text)
    if document_type == "form":
        return extract_form_fields(text)

    return {}
