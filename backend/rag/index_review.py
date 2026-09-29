import uuid

from backend.ingestion.cleaning import clean_review, review_hash
from backend.analysis.review_pipeline import process_review
from backend.rag.embeddings import generate_embedding
from backend.rag.search import get_search_client


def index_review(review_text: str) -> dict:

    # ---------------------------------------------------------
    # 1. Clean and hash FIRST
    # ---------------------------------------------------------

    cleaned_text = clean_review(review_text)

    if not cleaned_text:
        raise ValueError(
            "Review text is empty after cleaning."
        )

    current_review_hash = review_hash(
        cleaned_text
    )

    search_client = get_search_client()

    # ---------------------------------------------------------
    # 2. Check duplicate BEFORE calling Azure Language
    # ---------------------------------------------------------

    existing_results = search_client.search(
        search_text="*",
        filter=(
            f"review_hash eq "
            f"'{current_review_hash}'"
        ),
        select=[
            "id",
            "review_text",
            "review_hash",
        ],
        top=1,
    )

    existing_review = next(
        iter(existing_results),
        None,
    )

    if existing_review:

        return {
            "status": "duplicate",
            "message": (
                "Review already exists "
                "in Azure AI Search."
            ),
            "document_id": existing_review["id"],
            "review_hash": current_review_hash,
        }

    # ---------------------------------------------------------
    # 3. Only NEW reviews go through AI processing
    # ---------------------------------------------------------

    processed = process_review(
        review_text
    )

    # ---------------------------------------------------------
    # 4. Generate local embedding
    # ---------------------------------------------------------

    embedding = generate_embedding(
        processed["redacted_text"]
    )

    # ---------------------------------------------------------
    # 5. Create Search document
    # ---------------------------------------------------------

    document = {
        "id": str(uuid.uuid4()),

        "review_text": (
            processed["cleaned_text"]
        ),

        "redacted_text": (
            processed["redacted_text"]
        ),

        "sentiment": (
            processed["sentiment"]["sentiment"]
        ),

        "positive_score": (
            processed["sentiment"]["positive"]
        ),

        "neutral_score": (
            processed["sentiment"]["neutral"]
        ),

        "negative_score": (
            processed["sentiment"]["negative"]
        ),

        "review_hash": current_review_hash,

        "embedding": embedding,
    }

    # ---------------------------------------------------------
    # 6. Upload to Azure AI Search
    # ---------------------------------------------------------

    result = search_client.upload_documents(
        documents=[document]
    )

    return {
        "status": "indexed",
        "document": document,
        "upload_result": result,
    }