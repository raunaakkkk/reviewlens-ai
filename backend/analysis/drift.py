from datetime import datetime
from sqlalchemy import func

from backend.database import SessionLocal
from backend.models import Review, DriftResult


DRIFT_THRESHOLD = 0.20


def calculate_negative_rate(
    db,
    reviews,
    start_date=None,
    end_date=None,
):
    query = db.query(Review).filter(
        Review.sentiment.isnot(None)
    )

    if start_date:
        query = query.filter(
            Review.created_at >= start_date
        )

    if end_date:
        query = query.filter(
            Review.created_at < end_date
        )

    period_reviews = query.all()

    if not period_reviews:
        return {
            "sample_size": 0,
            "negative_count": 0,
            "negative_rate": 0.0,
        }

    negative_count = sum(
        1
        for review in period_reviews
        if review.sentiment.lower() == "negative"
    )

    negative_rate = (
        negative_count / len(period_reviews)
    )

    return {
        "sample_size": len(period_reviews),
        "negative_count": negative_count,
        "negative_rate": round(
            negative_rate,
            4,
        ),
    }


def calculate_drift():
    db = SessionLocal()

    try:
        all_reviews = (
            db.query(Review)
            .order_by(Review.created_at.asc())
            .all()
        )

        if len(all_reviews) < 2:
            return {
                "status": "insufficient_data",
                "message": (
                    "At least two reviews are required "
                    "for drift analysis."
                ),
            }

        midpoint = len(all_reviews) // 2

        baseline_reviews = all_reviews[:midpoint]
        current_reviews = all_reviews[midpoint:]

        baseline_negative = sum(
            1
            for review in baseline_reviews
            if review.sentiment.lower() == "negative"
        )

        current_negative = sum(
            1
            for review in current_reviews
            if review.sentiment.lower() == "negative"
        )

        baseline_rate = (
            baseline_negative / len(baseline_reviews)
        )

        current_rate = (
            current_negative / len(current_reviews)
        )

        change = current_rate - baseline_rate

        drift_detected = abs(change) >= DRIFT_THRESHOLD

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
            "baseline": {
                "sample_size": len(
                    baseline_reviews
                ),
                "negative_count": baseline_negative,
                "negative_rate": round(
                    baseline_rate,
                    4,
                ),
            },
            "current": {
                "sample_size": len(
                    current_reviews
                ),
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