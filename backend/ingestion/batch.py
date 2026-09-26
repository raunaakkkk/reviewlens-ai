import csv
from pathlib import Path

from backend.rag.index_review import index_review


def ingest_csv(csv_path: str) -> dict:
    """
    Read reviews from a CSV file and index them into Azure AI Search.

    Required CSV column:
        review_text

    Optional columns:
        review_id
        rating
        date
    """

    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(
            f"CSV file not found: {csv_path}"
        )

    total_reviews = 0
    indexed_reviews = 0
    duplicate_reviews = 0
    failed_reviews = 0

    failures = []

    # ---------------------------------------------------------
    # Read CSV
    # ---------------------------------------------------------

    with path.open(
        mode="r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file has no header.")

        if "review_text" not in reader.fieldnames:
            raise ValueError(
                "CSV must contain a 'review_text' column."
            )

        # -----------------------------------------------------
        # Process every review
        # -----------------------------------------------------

        for row_number, row in enumerate(reader, start=2):

            total_reviews += 1

            review_text = (
                row.get("review_text") or ""
            ).strip()

            if not review_text:
                failed_reviews += 1

                failures.append({
                    "row": row_number,
                    "error": "Empty review_text",
                })

                continue

            try:

                result = index_review(review_text)

                if result["status"] == "duplicate":

                    duplicate_reviews += 1

                    print(
                        f"[DUPLICATE] Row {row_number} "
                        f"already exists."
                    )

                elif result["status"] == "indexed":

                    indexed_reviews += 1

                    print(
                        f"[INDEXED] Row {row_number} "
                        f"successfully indexed."
                    )

                else:

                    failed_reviews += 1

                    failures.append({
                        "row": row_number,
                        "error": "Unknown indexing status",
                    })

            except Exception as exc:

                failed_reviews += 1

                failures.append({
                    "row": row_number,
                    "error": str(exc),
                })

                print(
                    f"[FAILED] Row {row_number}: {exc}"
                )

    # ---------------------------------------------------------
    # Final summary
    # ---------------------------------------------------------

    summary = {
        "total_reviews": total_reviews,
        "indexed_reviews": indexed_reviews,
        "duplicate_reviews": duplicate_reviews,
        "failed_reviews": failed_reviews,
        "failures": failures,
    }

    return summary


if __name__ == "__main__":

    csv_file = "data/reviews.csv"

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - BATCH INGESTION")
    print("=" * 60)

    summary = ingest_csv(csv_file)

    print("\n" + "=" * 60)
    print("INGESTION SUMMARY")
    print("=" * 60)

    print(
        "Total reviews       :",
        summary["total_reviews"]
    )

    print(
        "New reviews indexed :",
        summary["indexed_reviews"]
    )

    print(
        "Duplicates skipped  :",
        summary["duplicate_reviews"]
    )

    print(
        "Failed reviews      :",
        summary["failed_reviews"]
    )

    if summary["failures"]:

        print("\nFailures:")

        for failure in summary["failures"]:

            print(
                f"  Row {failure['row']}: "
                f"{failure['error']}"
            )

    print("=" * 60)