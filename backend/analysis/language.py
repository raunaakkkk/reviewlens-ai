import os
from typing import Any

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics import TextAnalyticsClient


load_dotenv()


LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")

if not LANGUAGE_ENDPOINT:
    raise RuntimeError(
        "AZURE_LANGUAGE_ENDPOINT is not configured"
    )


credential = DefaultAzureCredential()

language_client = TextAnalyticsClient(
    endpoint=LANGUAGE_ENDPOINT,
    credential=credential,
)


# =========================================================
# SINGLE-REVIEW FUNCTIONS
# Existing API preserved
# =========================================================

def redact_pii(text: str) -> dict:
    """
    Detect and redact personally identifiable information
    from one review.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    response = language_client.recognize_pii_entities(
        [text],
        language="en",
    )

    result = response[0]

    if result.is_error:
        raise RuntimeError(
            f"PII detection failed: {result.error}"
        )

    entities = []

    for entity in result.entities:
        entities.append(
            {
                "text": entity.text,
                "category": str(entity.category),
                "subcategory": entity.subcategory,
                "confidence_score": entity.confidence_score,
                "offset": entity.offset,
                "length": entity.length,
            }
        )

    return {
        "original_text": text,
        "redacted_text": result.redacted_text,
        "entities": entities,
    }


def analyze_sentiment(text: str) -> dict:
    """
    Analyze sentiment for one review.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    response = language_client.analyze_sentiment(
        [text],
        language="en",
    )

    result = response[0]

    if result.is_error:
        raise RuntimeError(
            f"Sentiment analysis failed: {result.error}"
        )

    return {
        "sentiment": result.sentiment,
        "positive": result.confidence_scores.positive,
        "neutral": result.confidence_scores.neutral,
        "negative": result.confidence_scores.negative,
    }


# =========================================================
# BATCH PII
# Azure Language limit: 5 documents/request
# =========================================================

def redact_pii_batch(
    texts: list[str],
) -> list[dict]:
    """
    Redact PII for multiple reviews.

    Azure Language PII synchronous limit:
        5 documents per request.

    The returned results preserve the same order
    as the input texts.
    """

    if not texts:
        return []

    if len(texts) > 5:
        raise ValueError(
            "redact_pii_batch accepts a maximum of "
            "5 documents per request."
        )

    response = language_client.recognize_pii_entities(
        texts,
        language="en",
    )

    results = []

    for index, result in enumerate(response):

        if result.is_error:
            raise RuntimeError(
                f"PII detection failed for document "
                f"{index}: {result.error}"
            )

        entities = []

        for entity in result.entities:
            entities.append(
                {
                    "text": entity.text,
                    "category": str(entity.category),
                    "subcategory": entity.subcategory,
                    "confidence_score": entity.confidence_score,
                    "offset": entity.offset,
                    "length": entity.length,
                }
            )

        results.append(
            {
                "original_text": texts[index],
                "redacted_text": result.redacted_text,
                "entities": entities,
            }
        )

    return results


# =========================================================
# BATCH SENTIMENT
# Azure Language limit: 10 documents/request
# =========================================================

def analyze_sentiment_batch(
    texts: list[str],
) -> list[dict]:
    """
    Analyze sentiment for multiple reviews.

    Azure Language sentiment synchronous limit:
        10 documents per request.

    The returned results preserve the same order
    as the input texts.
    """

    if not texts:
        return []

    if len(texts) > 10:
        raise ValueError(
            "analyze_sentiment_batch accepts a maximum "
            "of 10 documents per request."
        )

    response = language_client.analyze_sentiment(
        texts,
        language="en",
    )

    results = []

    for index, result in enumerate(response):

        if result.is_error:
            raise RuntimeError(
                f"Sentiment analysis failed for document "
                f"{index}: {result.error}"
            )

        results.append(
            {
                "sentiment": result.sentiment,
                "positive": result.confidence_scores.positive,
                "neutral": result.confidence_scores.neutral,
                "negative": result.confidence_scores.negative,
            }
        )

    return results