from sqlalchemy import select

from backend.database import SessionLocal
from backend.models import EvidenceLink, Insight, Review


def save_insights(
    insight_result: dict,
) -> dict:

    db = SessionLocal()

    try:
        themes = insight_result.get("themes", [])
        complaints = insight_result.get("complaints", [])
        evidence = insight_result.get("evidence", [])

        created_insights = 0
        created_links = 0

        def create_insight(
            insight_type: str,
            title: str,
            evidence_reason_prefix: str,
        ):
            nonlocal created_insights, created_links

            insight = Insight(
                insight_type=insight_type,
                title=title,
                description=(
                    f"{insight_type.capitalize()} identified "
                    f"from customer reviews: {title}"
                ),
            )

            db.add(insight)
            db.flush()

            created_insights += 1

            insight_words = set(
                title.lower().split()
            )

            for review_data in evidence:

                # Current evidence format uses "id".
                review_id = review_data.get(
                    "document_id",
                    review_data.get("id"),
                )

                if not review_id:
                    continue

                review_text = (
                    review_data.get(
                        "review_text",
                        ""
                    ).lower()
                )

                matching_words = [
                    word
                    for word in insight_words
                    if len(word) > 3
                ]

                if not matching_words:
                    continue

                if any(
                    word in review_text
                    for word in matching_words
                ):

                    review = db.execute(
                        select(Review).where(
                            Review.id == review_id
                        )
                    ).scalar_one_or_none()

                    if review:

                        link = EvidenceLink(
                            insight_id=insight.id,
                            review_id=review.id,
                            reason=(
                                f"{evidence_reason_prefix}: "
                                f"{title}"
                            ),
                            search_score=review_data.get(
                                "search_score",
                                review_data.get("score"),
                            ),
                        )

                        db.add(link)
                        created_links += 1

        # Create themes
        for theme in themes:
            create_insight(
                insight_type="theme",
                title=theme,
                evidence_reason_prefix="Review supports theme",
            )

        # Create complaints
        for complaint in complaints:
            create_insight(
                insight_type="complaint",
                title=complaint,
                evidence_reason_prefix="Review supports complaint",
            )

        db.commit()

        return {
            "insights_created": created_insights,
            "evidence_links_created": created_links,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":

    import re

    from backend.analysis.insights import generate_insights

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - INSIGHT TO POSTGRESQL SYNC")
    print("=" * 60)

    result = generate_insights(
        query=(
            "What are the main themes and complaints "
            "in these customer reviews?"
        ),
        top_k=4,
    )

    answer = result.get("answer", "")

    evidence_result = {
        "themes": [],
        "complaints": [],
        "evidence": result.get("evidence", []),
    }

    themes_match = re.search(
        r"THEMES:\s*(.*?)(?=COMPLAINTS:)",
        answer,
        re.DOTALL | re.IGNORECASE,
    )

    complaints_match = re.search(
        r"COMPLAINTS:\s*(.*?)(?=SUMMARY:)",
        answer,
        re.DOTALL | re.IGNORECASE,
    )

    if themes_match:
        evidence_result["themes"] = [
            line.strip()[1:].strip()
            for line in themes_match.group(1).splitlines()
            if line.strip().startswith("-")
        ]

    if complaints_match:
        evidence_result["complaints"] = [
            line.strip()[1:].strip()
            for line in complaints_match.group(1).splitlines()
            if line.strip().startswith("-")
        ]

    print("\nThemes:")
    for theme in evidence_result["themes"]:
        print(" -", theme)

    print("\nComplaints:")
    for complaint in evidence_result["complaints"]:
        print(" -", complaint)

    sync_result = save_insights(
        evidence_result
    )

    print("\nInsights created:")
    print(sync_result["insights_created"])

    print("Evidence links created:")
    print(sync_result["evidence_links_created"])

    print("\n" + "=" * 60)
    print("INSIGHT SYNC COMPLETE")
    print("=" * 60)