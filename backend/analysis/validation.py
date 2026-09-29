import csv
from pathlib import Path

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
)

from backend.analysis.language import analyze_sentiment


# =========================================================
# VALIDATION DATASET
# =========================================================

VALIDATION_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "validation"
    / "sentiment_validation.csv"
)


# =========================================================
# LOAD VALIDATION DATA
# =========================================================

def load_validation_data():

    if not VALIDATION_FILE.exists():

        raise FileNotFoundError(
            f"Validation file not found: {VALIDATION_FILE}"
        )

    reviews = []

    with open(
        VALIDATION_FILE,
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            text = row["review_text"].strip()

            true_sentiment = (
                row["true_sentiment"]
                .strip()
                .lower()
            )

            if not text:
                continue

            reviews.append(
                {
                    "review_text": text,
                    "true_sentiment": true_sentiment,
                }
            )

    return reviews


# =========================================================
# SENTIMENT VALIDATION
# =========================================================

def validate_sentiment():

    reviews = load_validation_data()

    y_true = []
    y_pred = []

    predictions = []

    for review in reviews:

        result = analyze_sentiment(
            review["review_text"]
        )

        predicted = result["sentiment"].lower()

        y_true.append(
            review["true_sentiment"]
        )

        y_pred.append(
            predicted
        )

        predictions.append(
            {
                "review_text": review["review_text"],
                "true_sentiment": review["true_sentiment"],
                "predicted_sentiment": predicted,
                "positive_score": result["positive"],
                "neutral_score": result["neutral"],
                "negative_score": result["negative"],
            }
        )

    accuracy = accuracy_score(
        y_true,
        y_pred,
    )

    precision = precision_score(
        y_true,
        y_pred,
        labels=[
            "positive",
            "neutral",
            "negative",
        ],
        average="weighted",
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        labels=[
            "positive",
            "neutral",
            "negative",
        ],
        average="weighted",
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        labels=[
            "positive",
            "neutral",
            "negative",
        ],
        average="weighted",
        zero_division=0,
    )

    report = classification_report(
        y_true,
        y_pred,
        labels=[
            "positive",
            "neutral",
            "negative",
        ],
        zero_division=0,
    )

    return {
        "status": "success",
        "sample_size": len(reviews),
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "classification_report": report,
        "predictions": predictions,
    }


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    result = validate_sentiment()

    print("\n========================================")
    print("SENTIMENT VALIDATION")
    print("========================================")

    print(
        "Sample size :",
        result["sample_size"],
    )

    print(
        "Accuracy    :",
        result["accuracy"],
    )

    print(
        "Precision   :",
        result["precision"],
    )

    print(
        "Recall      :",
        result["recall"],
    )

    print(
        "F1 Score    :",
        result["f1"],
    )

    print("\nClassification Report:")

    print(
        result["classification_report"]
    )