import hashlib
import re
from typing import Any


def normalize_text(text: str) -> str:
    """
    Basic normalization of review text.
    """

    if not text:
        return ""

    # Convert to string and remove leading/trailing whitespace
    text = str(text).strip()

    # Normalize line breaks
    text = re.sub(r"[\r\n\t]+", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text


def clean_review(text: str) -> str:
    """
    Clean a single review.
    """

    text = normalize_text(text)

    # Remove obvious HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Normalize whitespace again
    text = re.sub(r"\s+", " ", text).strip()

    return text


def review_hash(text: str) -> str:
    """
    Generate a deterministic hash for duplicate detection.
    """

    normalized = clean_review(text).lower()

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def deduplicate_reviews(reviews: list[str]) -> list[str]:
    """
    Remove duplicate reviews while preserving order.
    """

    unique_reviews = []
    seen_hashes = set()

    for review in reviews:
        cleaned = clean_review(review)

        if not cleaned:
            continue

        current_hash = review_hash(cleaned)

        if current_hash in seen_hashes:
            continue

        seen_hashes.add(current_hash)
        unique_reviews.append(cleaned)

    return unique_reviews


def clean_review_records(
    records: list[dict[str, Any]],
    text_field: str = "text",
) -> list[dict[str, Any]]:
    """
    Clean and deduplicate review records.

    Example input:
    [
        {"id": 1, "text": "Great product!"},
        {"id": 2, "text": "Great product!"},
    ]
    """

    cleaned_records = []
    seen_hashes = set()

    for record in records:
        if text_field not in record:
            continue

        cleaned_text = clean_review(record[text_field])

        if not cleaned_text:
            continue

        current_hash = review_hash(cleaned_text)

        if current_hash in seen_hashes:
            continue

        seen_hashes.add(current_hash)

        cleaned_record = dict(record)
        cleaned_record[text_field] = cleaned_text
        cleaned_record["review_hash"] = current_hash

        cleaned_records.append(cleaned_record)

    return cleaned_records