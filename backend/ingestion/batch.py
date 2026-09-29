import csv
import uuid
from pathlib import Path

from backend.ingestion.cleaning import clean_review, review_hash
from backend.analysis.language import (
    redact_pii_batch,
    analyze_sentiment_batch,
)
from backend.rag.embeddings import generate_embeddings
from backend.rag.search import get_search_client


# =========================================================
# CONFIGURATION
# =========================================================

PROCESS_BATCH_SIZE = 10
PII_BATCH_SIZE = 5
SENTIMENT_BATCH_SIZE = 10
EMBEDDING_BATCH_SIZE = 32
SEARCH_UPLOAD_BATCH_SIZE = 500


# =========================================================
# LOAD EXISTING REVIEW HASHES
# =========================================================

def load_existing_hashes(search_client) -> set[str]:
    """
    Load all existing review hashes from Azure AI Search.

    Uses pagination instead of top=1000 so datasets larger
    than 1,000 reviews are handled correctly.
    """

    existing_hashes = set()

    results = search_client.search(
        search_text="*",
        select=["review_hash"],
        top=1000,
    )

    for result in results:
        value = result.get("review_hash")

        if value:
            existing_hashes.add(value)

    return existing_hashes


# =========================================================
# UPLOAD SEARCH DOCUMENTS IN SAFE BATCHES
# =========================================================

def upload_search_documents(
    search_client,
    documents: list[dict],
) -> int:
    """
    Upload Search documents in batches.

    Azure AI Search supports large indexing requests, but
    smaller batches provide better safety for production
    ingestion.
    """

    uploaded = 0

    for start in range(
        0,
        len(documents),
        SEARCH_UPLOAD_BATCH_SIZE,
    ):

        batch = documents[
            start:
            start + SEARCH_UPLOAD_BATCH_SIZE
        ]

        result = search_client.upload_documents(
            documents=batch
        )

        # Check individual indexing results.
        for item in result:

            if item.succeeded:
                uploaded += 1

            else:
                raise RuntimeError(
                    "Azure AI Search indexing failed "
                    f"for document {item.key}: "
                    f"{item.error_message}"
                )

    return uploaded


# =========================================================
# CSV INGESTION
# =========================================================

def ingest_csv(csv_path: str) -> dict:
    """
    Process a CSV containing review_text.

    Pipeline:

        CSV
        ↓
        Cleaning
        ↓
        Local duplicate filtering
        ↓
        PII redaction
        ↓
        Sentiment analysis
        ↓
        Batch embeddings
        ↓
        Azure AI Search batch upload
    """

    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}"
        )

    search_client = get_search_client()

    total_reviews = 0
    indexed_reviews = 0
    duplicate_reviews = 0
    failed_reviews = 0

    failures = []

    # =====================================================
    # LOAD EXISTING HASHES ONCE
    # =====================================================

    print(
        "[INGESTION] Loading existing review hashes..."
    )

    existing_hashes = load_existing_hashes(
        search_client
    )

    print(
        "[INGESTION] Existing hashes loaded: "
        f"{len(existing_hashes)}"
    )

    # =====================================================
    # READ CSV
    # =====================================================

    pending_reviews = []

    with path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError(
                "CSV file has no header."
            )

        if "review_text" not in reader.fieldnames:
            raise ValueError(
                "CSV must contain a 'review_text' column."
            )

        for row_number, row in enumerate(
            reader,
            start=2,
        ):

            total_reviews += 1

            review_text = (
                row.get("review_text") or ""
            ).strip()

            if not review_text:

                failed_reviews += 1

                failures.append(
                    {
                        "row": row_number,
                        "error": "Empty review_text",
                    }
                )

                continue

            try:

                cleaned_text = clean_review(
                    review_text
                )

                if not cleaned_text:

                    failed_reviews += 1

                    failures.append(
                        {
                            "row": row_number,
                            "error": (
                                "Review text is empty "
                                "after cleaning"
                            ),
                        }
                    )

                    continue

                current_hash = review_hash(
                    cleaned_text
                )

                # -------------------------------------------------
                # Existing Search duplicate
                # -------------------------------------------------

                if current_hash in existing_hashes:

                    duplicate_reviews += 1
                    continue

                # -------------------------------------------------
                # Duplicate inside current CSV
                # -------------------------------------------------

                if any(
                    item["review_hash"]
                    == current_hash
                    for item in pending_reviews
                ):

                    duplicate_reviews += 1
                    continue

                pending_reviews.append(
                    {
                        "row_number": row_number,
                        "original_text": review_text,
                        "cleaned_text": cleaned_text,
                        "review_hash": current_hash,
                    }
                )

                # Add immediately so duplicates later
                # in the same CSV are detected locally.
                existing_hashes.add(
                    current_hash
                )

            except Exception as exc:

                failed_reviews += 1

                failures.append(
                    {
                        "row": row_number,
                        "error": str(exc),
                    }
                )

    print(
        "[INGESTION] CSV reviews: "
        f"{total_reviews}"
    )

    print(
        "[INGESTION] New reviews: "
        f"{len(pending_reviews)}"
    )

    print(
        "[INGESTION] Duplicates: "
        f"{duplicate_reviews}"
    )

    # =====================================================
    # PROCESS NEW REVIEWS
    # =====================================================

    for batch_start in range(
        0,
        len(pending_reviews),
        PROCESS_BATCH_SIZE,
    ):

        batch = pending_reviews[
            batch_start:
            batch_start + PROCESS_BATCH_SIZE
        ]

        try:

            # =================================================
            # PII REDACTION
            # =================================================

            pii_results = []

            for start in range(
                0,
                len(batch),
                PII_BATCH_SIZE,
            ):

                pii_batch = batch[
                    start:
                    start + PII_BATCH_SIZE
                ]

                pii_texts = [
                    item["cleaned_text"]
                    for item in pii_batch
                ]

                pii_results.extend(
                    redact_pii_batch(
                        pii_texts
                    )
                )

            # =================================================
            # SENTIMENT
            # =================================================

            sentiment_texts = [
                result["redacted_text"]
                for result in pii_results
            ]

            sentiment_results = []

            for start in range(
                0,
                len(sentiment_texts),
                SENTIMENT_BATCH_SIZE,
            ):

                sentiment_batch = (
                    sentiment_texts[
                        start:
                        start + SENTIMENT_BATCH_SIZE
                    ]
                )

                sentiment_results.extend(
                    analyze_sentiment_batch(
                        sentiment_batch
                    )
                )

            # =================================================
            # EMBEDDINGS
            # =================================================

            embeddings = generate_embeddings(
                sentiment_texts,
                batch_size=EMBEDDING_BATCH_SIZE,
            )

            # =================================================
            # BUILD SEARCH DOCUMENTS
            # =================================================

            documents = []

            for index, item in enumerate(batch):

                pii_result = pii_results[index]

                sentiment_result = (
                    sentiment_results[index]
                )

                document = {
                    "id": str(uuid.uuid4()),

                    "review_text": item[
                        "cleaned_text"
                    ],

                    "redacted_text": pii_result[
                        "redacted_text"
                    ],

                    "sentiment": sentiment_result[
                        "sentiment"
                    ],

                    "positive_score": sentiment_result[
                        "positive"
                    ],

                    "neutral_score": sentiment_result[
                        "neutral"
                    ],

                    "negative_score": sentiment_result[
                        "negative"
                    ],

                    "review_hash": item[
                        "review_hash"
                    ],

                    "embedding": embeddings[index],
                }

                documents.append(document)

            # =================================================
            # SEARCH UPLOAD
            # =================================================

            uploaded = upload_search_documents(
                search_client,
                documents,
            )

            indexed_reviews += uploaded

            # =================================================
            # PROGRESS
            # =================================================

            processed_count = min(
                batch_start + len(batch),
                len(pending_reviews),
            )

            print(
                "[INGESTION] "
                f"Processed {processed_count}/"
                f"{len(pending_reviews)} | "
                f"Indexed: {indexed_reviews} | "
                f"Duplicates: {duplicate_reviews} | "
                f"Failed: {failed_reviews}"
            )

        except Exception as exc:

            for item in batch:

                failed_reviews += 1

                failures.append(
                    {
                        "row": item["row_number"],
                        "error": str(exc),
                    }
                )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    return {
        "status": "success",
        "total_reviews": total_reviews,
        "indexed_reviews": indexed_reviews,
        "duplicate_reviews": duplicate_reviews,
        "failed_reviews": failed_reviews,
        "failures": failures[:100],
    }