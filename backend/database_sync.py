from sqlalchemy import select

from backend.database import SessionLocal
from backend.models import Review


def save_review_to_database(review: dict) -> bool:
    """
    Save one Azure AI Search review into PostgreSQL.

    Returns:
        True  -> inserted
        False -> already exists
    """

    db = SessionLocal()

    try:
        review_id = review["id"]
        review_hash = review["review_hash"]

        existing = db.execute(
            select(Review).where(
                Review.review_hash == review_hash
            )
        ).scalar_one_or_none()

        if existing:
            return False

        db_review = Review(
            id=review_id,
            review_hash=review_hash,
            review_text=review["review_text"],
            redacted_text=review["redacted_text"],
            sentiment=review["sentiment"],
            positive_score=review["positive_score"],
            neutral_score=review["neutral_score"],
            negative_score=review["negative_score"],
        )

        db.add(db_review)
        db.commit()

        return True

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def sync_reviews_to_database(
    reviews: list[dict],
) -> dict:

    inserted = 0
    skipped = 0

    for review in reviews:

        if save_review_to_database(review):
            inserted += 1
        else:
            skipped += 1

    return {
        "total": len(reviews),
        "inserted": inserted,
        "skipped": skipped,
    }


if __name__ == "__main__":

    from backend.rag.retrieve import retrieve_reviews

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - SEARCH TO POSTGRESQL SYNC")
    print("=" * 60)

    reviews = retrieve_reviews(
        query="customer reviews",
        top_k=10,
    )

    result = sync_reviews_to_database(
        reviews
    )

    print("\nTotal retrieved :", result["total"])
    print("Inserted        :", result["inserted"])
    print("Skipped         :", result["skipped"])

    print("\n" + "=" * 60)