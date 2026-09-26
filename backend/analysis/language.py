import os

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


def redact_pii(text: str) -> dict:
    """
    Detect and redact personally identifiable information.
    """

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
    Analyze review sentiment.
    """

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