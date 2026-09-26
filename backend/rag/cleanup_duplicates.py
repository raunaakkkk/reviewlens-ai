from collections import defaultdict

from backend.rag.search import get_search_client


def find_duplicate_reviews() -> dict:
    """
    Find duplicate documents in Azure AI Search
    based on review_hash.
    """

    search_client = get_search_client()

    results = search_client.search(
        search_text="*",
        select=[
            "id",
            "review_text",
            "redacted_text",
            "sentiment",
            "review_hash",
        ],
        top=1000,
    )

    grouped = defaultdict(list)

    for document in results:
        review_hash = document.get("review_hash")

        if not review_hash:
            continue

        grouped[review_hash].append(document)

    duplicates = {
        review_hash: documents
        for review_hash, documents in grouped.items()
        if len(documents) > 1
    }

    return duplicates


def delete_duplicate_documents(
    duplicates: dict,
    dry_run: bool = True,
) -> dict:
    """
    Delete duplicate documents.

    dry_run=True:
        Only show what would be deleted.

    dry_run=False:
        Actually delete duplicates.
    """

    search_client = get_search_client()

    deleted = []
    kept = []

    for review_hash, documents in duplicates.items():

        # Keep the first document.
        documents_to_keep = documents[0]

        kept.append({
            "review_hash": review_hash,
            "document_id": documents_to_keep["id"],
        })

        # Delete the remaining documents.
        for document in documents[1:]:

            document_id = document["id"]

            print(
                f"{'[DRY RUN] Would delete' if dry_run else 'Deleting'}: "
                f"{document_id}"
            )

            if not dry_run:

                result = search_client.delete_documents(
                    documents=[
                        {
                            "id": document_id
                        }
                    ]
                )

                deleted.append({
                    "document_id": document_id,
                    "result": result,
                })

    return {
        "kept": kept,
        "deleted": deleted,
    }


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - DUPLICATE CLEANUP")
    print("=" * 60)

    duplicates = find_duplicate_reviews()

    if not duplicates:

        print("\nNo duplicate reviews found.")

    else:

        print(
            f"\nFound {len(duplicates)} "
            f"duplicate review group(s).\n"
        )

        for review_hash, documents in duplicates.items():

            print("-" * 60)

            print(
                "Review hash:",
                review_hash
            )

            print(
                "Documents:",
                len(documents)
            )

            for document in documents:

                print(
                    "  ID:",
                    document["id"]
                )

                print(
                    "  Review:",
                    document["redacted_text"]
                )

    # ---------------------------------------------------------
    # SAFETY: First run is DRY RUN
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("DRY RUN - NO DOCUMENTS WILL BE DELETED")
    print("=" * 60)

    result = delete_duplicate_documents(
        duplicates,
        dry_run=True,
    )

    print("\nDocuments to keep:")

    for item in result["kept"]:

        print(
            "  ",
            item["document_id"]
        )

    print("\nRun completed safely.")