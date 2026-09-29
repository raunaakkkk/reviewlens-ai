from backend.analysis.insights import generate_insights
from backend.analysis.evidence import build_evidence_links

from backend.database import SessionLocal
from backend.models import Review, Insight, EvidenceLink


def remove_existing_generated_insights(db):
    """
    Remove previously generated theme/complaint insights
    and their evidence links.

    This prevents duplicate/stale insights from accumulating.
    """

    existing_insights = (
        db.query(Insight)
        .filter(
            Insight.insight_type.in_(
                ["theme", "complaint"]
            )
        )
        .all()
    )

    for insight in existing_insights:
        db.delete(insight)

    db.flush()


def sync_insights() -> dict:
    """
    Generate fresh AI insights and replace the previous
    generated insights in PostgreSQL.
    """

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # Generate fresh insights
        # -------------------------------------------------

        insight_result = generate_insights(
            query=(
                "What are the main themes and complaints "
                "in these customer reviews?"
            ),
            top_k=10,
        )

        if insight_result.get("status") != "success":

            return {
                "status": "no_data",
                "created": 0,
                "skipped": 0,
                "evidence_links": 0,
            }

        linked_result = build_evidence_links(
            insight_result
        )

        themes = linked_result.get(
            "themes",
            []
        )

        complaints = linked_result.get(
            "complaints",
            []
        )

        evidence = linked_result.get(
            "evidence",
            []
        )

        # -------------------------------------------------
        # Remove old generated insights
        # -------------------------------------------------

        remove_existing_generated_insights(
            db
        )

        created = 0
        evidence_created = 0

        # -------------------------------------------------
        # Remove exact duplicate items from Qwen output
        # -------------------------------------------------

        unique_themes = []
        seen_themes = set()

        for theme in themes:

            normalized = theme.strip().lower()

            if not normalized:
                continue

            if normalized in seen_themes:
                continue

            seen_themes.add(normalized)
            unique_themes.append(theme.strip())

        unique_complaints = []
        seen_complaints = set()

        for complaint in complaints:

            normalized = complaint.strip().lower()

            if not normalized:
                continue

            if normalized in seen_complaints:
                continue

            seen_complaints.add(normalized)
            unique_complaints.append(
                complaint.strip()
            )

        # -------------------------------------------------
        # Create theme insights
        # -------------------------------------------------

        for theme in unique_themes:

            insight = Insight(
                insight_type="theme",
                title=theme,
                description=(
                    "Theme identified from "
                    f"customer reviews: {theme}"
                ),
            )

            db.add(insight)
            db.flush()

            created += 1

            # Link supporting reviews
            for review in evidence:

                review_id = review.get(
                    "document_id"
                )

                if not review_id:
                    continue

                db_review = (
                    db.query(Review)
                    .filter(
                        Review.id == review_id
                    )
                    .first()
                )

                if not db_review:
                    continue

                link = EvidenceLink(
                    insight_id=insight.id,
                    review_id=review_id,
                    reason=(
                        "Review evidence supporting "
                        f"theme: {theme}"
                    ),
                    search_score=review.get(
                        "search_score"
                    ),
                )

                db.add(link)

                evidence_created += 1

        # -------------------------------------------------
        # Create complaint insights
        # -------------------------------------------------

        for complaint in unique_complaints:

            insight = Insight(
                insight_type="complaint",
                title=complaint,
                description=(
                    "Complaint identified from "
                    f"customer reviews: {complaint}"
                ),
            )

            db.add(insight)
            db.flush()

            created += 1

            # Link supporting reviews
            for review in evidence:

                review_id = review.get(
                    "document_id"
                )

                if not review_id:
                    continue

                db_review = (
                    db.query(Review)
                    .filter(
                        Review.id == review_id
                    )
                    .first()
                )

                if not db_review:
                    continue

                link = EvidenceLink(
                    insight_id=insight.id,
                    review_id=review_id,
                    reason=(
                        "Review evidence supporting "
                        f"complaint: {complaint}"
                    ),
                    search_score=review.get(
                        "search_score"
                    ),
                )

                db.add(link)

                evidence_created += 1

        # -------------------------------------------------
        # Save
        # -------------------------------------------------

        db.commit()

        return {
            "status": "success",
            "created": created,
            "skipped": 0,
            "evidence_links": evidence_created,
            "themes": unique_themes,
            "complaints": unique_complaints,
        }

    except Exception:

        db.rollback()
        raise

    finally:

        db.close()


if __name__ == "__main__":

    result = sync_insights()

    print("\nINSIGHT SYNC COMPLETE")
    print(
        "Created        :",
        result.get("created")
    )
    print(
        "Skipped        :",
        result.get("skipped")
    )
    print(
        "Evidence links :",
        result.get("evidence_links")
    )

    print("\nThemes:")

    for theme in result.get(
        "themes",
        []
    ):
        print(" -", theme)

    print("\nComplaints:")

    for complaint in result.get(
        "complaints",
        []
    ):
        print(" -", complaint)