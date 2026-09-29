from backend.rag.search import get_search_client
from backend.database import SessionLocal
from backend.models import Review


def sync_search_to_database() -> dict:
    """
    Synchronize reviews from Azure AI Search to PostgreSQL.

    Existing reviews are skipped using review_hash.
    """

    search_client = get_search_client()
    db = SessionLocal()

    inserted = 0
    skipped = 0

    try:
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
            top=1000,
        )

        for result in results:

            review_hash = result.get("review_hash")

            if not review_hash:
                continue

            existing = (
                db.query(Review)
                .filter(
                    Review.review_hash == review_hash
                )
                .first()
            )

            if existing:
                skipped += 1
                continue

            review = Review(
                id=result["id"],
                review_hash=review_hash,
                review_text=result["review_text"],
                redacted_text=result["redacted_text"],
                sentiment=result["sentiment"],
                positive_score=result["positive_score"],
                neutral_score=result["neutral_score"],
                negative_score=result["negative_score"],
            )

            db.add(review)
            inserted += 1

        db.commit()

        return {
            "status": "success",
            "inserted": inserted,
            "skipped": skipped,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":

    result = sync_search_to_database()

    print("DATABASE SYNC COMPLETE")
    print("Inserted :", result["inserted"])
    print("Skipped  :", result["skipped"])