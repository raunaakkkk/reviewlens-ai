from backend.rag.search import get_search_client
from backend.database import SessionLocal
from backend.models import Review


SEARCH_PAGE_SIZE = 1000
DB_BATCH_SIZE = 500


def get_search_reviews(search_client) -> list[dict]:
    """
    Retrieve ALL reviews from Azure AI Search using
    explicit pagination.
    """

    reviews = []
    skip = 0

    while True:

        results = search_client.search(
            search_text="*",
            select=[
                "id",
                "review_text",
                "redacted_text",
                "sentiment",
                "positive_score",
                "neutral_score",
                "negative_score",
                "review_hash",
            ],
            top=SEARCH_PAGE_SIZE,
            skip=skip,
        )

        page_count = 0

        for result in results:

            review_hash = result.get("review_hash")

            if not review_hash:
                continue

            reviews.append(
                {
                    "id": result["id"],
                    "review_hash": review_hash,
                    "review_text": result["review_text"],
                    "redacted_text": result["redacted_text"],
                    "sentiment": result["sentiment"],
                    "positive_score": result[
                        "positive_score"
                    ],
                    "neutral_score": result[
                        "neutral_score"
                    ],
                    "negative_score": result[
                        "negative_score"
                    ],
                }
            )

            page_count += 1

        print(
            f"[DATABASE] Retrieved Search page: "
            f"{page_count} | Total: {len(reviews)}"
        )

        if page_count < SEARCH_PAGE_SIZE:
            break

        skip += SEARCH_PAGE_SIZE

    return reviews


def sync_search_to_database() -> dict:
    """
    Synchronize all Azure AI Search reviews to PostgreSQL.
    """

    search_client = get_search_client()
    db = SessionLocal()

    inserted = 0
    skipped = 0

    try:

        # =================================================
        # GET ALL SEARCH REVIEWS
        # =================================================

        search_reviews = get_search_reviews(
            search_client
        )

        print(
            "[DATABASE] Total Search reviews: "
            f"{len(search_reviews)}"
        )

        if not search_reviews:

            return {
                "status": "success",
                "inserted": 0,
                "skipped": 0,
                "search_reviews": 0,
            }

        # =================================================
        # GET EXISTING DATABASE HASHES
        # =================================================

        existing_hash_rows = (
            db.query(Review.review_hash).all()
        )

        existing_hashes = {
            row[0]
            for row in existing_hash_rows
            if row[0]
        }

        print(
            "[DATABASE] Existing DB hashes: "
            f"{len(existing_hashes)}"
        )

        # =================================================
        # FIND NEW REVIEWS
        # =================================================

        new_reviews = []

        for result in search_reviews:

            review_hash = result["review_hash"]

            if review_hash in existing_hashes:

                skipped += 1
                continue

            new_reviews.append(
                Review(
                    id=result["id"],
                    review_hash=review_hash,
                    review_text=result["review_text"],
                    redacted_text=result[
                        "redacted_text"
                    ],
                    sentiment=result["sentiment"],
                    positive_score=result[
                        "positive_score"
                    ],
                    neutral_score=result[
                        "neutral_score"
                    ],
                    negative_score=result[
                        "negative_score"
                    ],
                )
            )

            existing_hashes.add(review_hash)

        # =================================================
        # BULK INSERT
        # =================================================

        for start in range(
            0,
            len(new_reviews),
            DB_BATCH_SIZE,
        ):

            batch = new_reviews[
                start:
                start + DB_BATCH_SIZE
            ]

            db.add_all(batch)
            db.commit()

            inserted += len(batch)

            print(
                "[DATABASE] Inserted "
                f"{inserted}/{len(new_reviews)}"
            )

        # =================================================
        # FINAL RESULT
        # =================================================

        return {
            "status": "success",
            "inserted": inserted,
            "skipped": skipped,
            "search_reviews": len(
                search_reviews
            ),
        }

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()