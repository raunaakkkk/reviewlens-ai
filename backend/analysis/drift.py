from datetime import datetime, timezone

from backend.database import SessionLocal
from backend.models import Review, DriftResult


DRIFT_THRESHOLD = 0.20


def calculate_drift():
    db = SessionLocal()

    try:
        all_reviews = (
            db.query(Review)
            .filter(Review.sentiment.isnot(None))
            .order_by(Review.created_at.asc(), Review.id.asc())
            .all()
        )

        total_reviews = len(all_reviews)

        if total_reviews < 2:
            return {
                "status": "insufficient_data",
                "message": (
                    "At least two reviews are required "
                    "for drift analysis."
                ),
            }

        # Split the CURRENT dataset into two equal parts.
        midpoint = total_reviews // 2

        baseline_reviews = all_reviews[:midpoint]
        current_reviews = all_reviews[midpoint:]

        baseline_negative = sum(
            1
            for review in baseline_reviews
            if review.sentiment
            and review.sentiment.lower() == "negative"
        )

        current_negative = sum(
            1
            for review in current_reviews
            if review.sentiment
            and review.sentiment.lower() == "negative"
        )

        baseline_rate = (
            baseline_negative / len(baseline_reviews)
        )

        current_rate = (
            current_negative / len(current_reviews)
        )

        change = current_rate - baseline_rate

        drift_detected = abs(change) >= DRIFT_THRESHOLD

        # These timestamps describe the records used for each half.
        baseline_period = (
            f"{baseline_reviews[0].created_at.isoformat()}"
            f" to "
            f"{baseline_reviews[-1].created_at.isoformat()}"
        )

        current_period = (
            f"{current_reviews[0].created_at.isoformat()}"
            f" to "
            f"{current_reviews[-1].created_at.isoformat()}"
        )

        result = DriftResult(
            current_period=current_period,
            baseline_period=baseline_period,
            baseline_negative_rate=round(
                baseline_rate,
                4,
            ),
            current_negative_rate=round(
                current_rate,
                4,
            ),
            negative_rate_change=round(
                change,
                4,
            ),
            drift_detected=drift_detected,
        )

        db.add(result)
        db.commit()
        db.refresh(result)

        return {
            "status": "success",
            "id": result.id,

            "dataset": {
                "total_reviews": total_reviews,
                "baseline_reviews": len(baseline_reviews),
                "current_reviews": len(current_reviews),
                "calculated_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            },

            "baseline": {
                "sample_size": len(baseline_reviews),
                "negative_count": baseline_negative,
                "negative_rate": round(
                    baseline_rate,
                    4,
                ),
            },

            "current": {
                "sample_size": len(current_reviews),
                "negative_count": current_negative,
                "negative_rate": round(
                    current_rate,
                    4,
                ),
            },

            "negative_rate_change": round(
                change,
                4,
            ),

            "threshold": DRIFT_THRESHOLD,

            "drift_detected": drift_detected,

            "baseline_period": baseline_period,
            "current_period": current_period,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    print("\n============================================================")
    print("REVIEWLENS AI - DRIFT MONITORING")
    print("============================================================")

    result = calculate_drift()

    print("\nStatus:", result["status"])

    if result["status"] == "success":
        print(
            "Total reviews:",
            result["dataset"]["total_reviews"],
        )

        print(
            "Baseline reviews:",
            result["dataset"]["baseline_reviews"],
        )

        print(
            "Current reviews:",
            result["dataset"]["current_reviews"],
        )

        print(
            "Baseline negative rate:",
            result["baseline"]["negative_rate"],
        )

        print(
            "Current negative rate:",
            result["current"]["negative_rate"],
        )

        print(
            "Negative rate change:",
            result["negative_rate_change"],
        )

        print(
            "Drift threshold:",
            result["threshold"],
        )

        print(
            "Drift detected:",
            result["drift_detected"],
        )

    else:
        print(
            result.get(
                "message",
                "Drift analysis could not be completed.",
            )
        )