import uuid

from backend.analysis.review_pipeline import process_review
from backend.ingestion.cleaning import review_hash
from backend.rag.embeddings import generate_embedding
from backend.rag.search import get_search_client


def index_review(review_text: str) -> dict:
    """
    Process a review and index it into Azure AI Search.

    Pipeline:
    Review
      ↓
    Cleaning
      ↓
    Hash generation
      ↓
    Duplicate check
      ↓
    PII Redaction
      ↓
    Sentiment Analysis
      ↓
    Embedding
      ↓
    Azure AI Search
    """

    # ---------------------------------------------------------
    # 1. Clean + PII redaction + sentiment analysis
    # ---------------------------------------------------------

    processed = process_review(review_text)

    cleaned_text = processed["cleaned_text"]

    if not cleaned_text:
        raise ValueError("Review text is empty after cleaning.")

    # ---------------------------------------------------------
    # 2. Generate deterministic hash
    # ---------------------------------------------------------

    current_review_hash = review_hash(cleaned_text)

    # ---------------------------------------------------------
    # 3. Get Azure AI Search client
    # ---------------------------------------------------------

    search_client = get_search_client()

    # ---------------------------------------------------------
    # 4. Check whether this review already exists
    # ---------------------------------------------------------

    existing_results = search_client.search(
        search_text="*",
        filter=f"review_hash eq '{current_review_hash}'",
        select=[
            "id",
            "review_text",
            "review_hash",
        ],
        top=1,
    )

    existing_review = next(iter(existing_results), None)

    if existing_review:
        return {
            "status": "duplicate",
            "message": "Review already exists in Azure AI Search.",
            "document_id": existing_review["id"],
            "review_hash": current_review_hash,
        }

    # ---------------------------------------------------------
    # 5. Generate embedding
    # ---------------------------------------------------------

    embedding = generate_embedding(
        processed["redacted_text"]
    )

    # ---------------------------------------------------------
    # 6. Create new Azure AI Search document
    # ---------------------------------------------------------

    document = {
        "id": str(uuid.uuid4()),

        "review_text": processed["cleaned_text"],

        "redacted_text": processed["redacted_text"],

        "sentiment": processed["sentiment"]["sentiment"],

        "positive_score": processed["sentiment"]["positive"],

        "neutral_score": processed["sentiment"]["neutral"],

        "negative_score": processed["sentiment"]["negative"],

        "review_hash": current_review_hash,

        "embedding": embedding,
    }

    # ---------------------------------------------------------
    # 7. Upload document
    # ---------------------------------------------------------

    result = search_client.upload_documents(
        documents=[document]
    )

    # ---------------------------------------------------------
    # 8. Return result
    # ---------------------------------------------------------

    return {
        "status": "indexed",
        "document": document,
        "upload_result": result,
    }


if __name__ == "__main__":

    review = (
        "The product works well, but delivery was late "
        "and customer support did not respond to my complaint."
    )

    result = index_review(review)

    print("\n" + "=" * 60)

    if result["status"] == "duplicate":

        print("DUPLICATE REVIEW DETECTED")

        print(
            "Message:",
            result["message"]
        )

        print(
            "Existing Document ID:",
            result["document_id"]
        )

        print(
            "Review hash:",
            result["review_hash"]
        )

    else:

        document = result["document"]

        print("NEW REVIEW INDEXED SUCCESSFULLY")

        print(
            "Document ID:",
            document["id"]
        )

        print(
            "Sentiment:",
            document["sentiment"]
        )

        print(
            "Embedding dimension:",
            len(document["embedding"])
        )

        print(
            "Review hash:",
            document["review_hash"]
        )

        print(
            "Redacted review:",
            document["redacted_text"]
        )

    print("=" * 60)