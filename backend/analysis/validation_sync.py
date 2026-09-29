from backend.analysis.validation import validate_sentiment
from backend.database import SessionLocal
from backend.models import ValidationResult


def sync_validation_result():

    result = validate_sentiment()

    if result.get("status") != "success":
        raise RuntimeError(
            "Sentiment validation failed."
        )

    db = SessionLocal()

    try:

        validation = ValidationResult(
            sample_size=result["sample_size"],
            accuracy=result["accuracy"],
            precision=result["precision"],
            recall=result["recall"],
            f1_score=result["f1"],
        )

        db.add(validation)
        db.commit()
        db.refresh(validation)

        return {
            "status": "success",
            "id": validation.id,
            "sample_size": validation.sample_size,
            "accuracy": validation.accuracy,
            "precision": validation.precision,
            "recall": validation.recall,
            "f1": validation.f1_score,
        }

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":

    result = sync_validation_result()

    print("\n========================================")
    print("VALIDATION RESULT SAVED")
    print("========================================")

    print("ID          :", result["id"])
    print("Sample size :", result["sample_size"])
    print("Accuracy    :", result["accuracy"])
    print("Precision   :", result["precision"])
    print("Recall      :", result["recall"])
    print("F1 Score    :", result["f1"])