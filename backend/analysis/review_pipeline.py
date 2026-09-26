from backend.ingestion.cleaning import clean_review
from backend.analysis.language import redact_pii, analyze_sentiment


def process_review(text: str) -> dict:
    """
    Process one review through:

    1. Cleaning
    2. PII redaction
    3. Sentiment analysis
    """

    # Step 1: Clean
    cleaned_text = clean_review(text)

    if not cleaned_text:
        raise ValueError("Review text is empty after cleaning.")

    # Step 2: PII redaction
    pii_result = redact_pii(cleaned_text)

    redacted_text = pii_result["redacted_text"]

    # Step 3: Sentiment analysis on redacted text
    sentiment_result = analyze_sentiment(redacted_text)

    return {
        "original_text": text,
        "cleaned_text": cleaned_text,
        "redacted_text": redacted_text,
        "pii_entities": pii_result["entities"],
        "sentiment": sentiment_result,
    }