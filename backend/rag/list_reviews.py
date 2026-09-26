from backend.rag.search import get_search_client


if __name__ == "__main__":

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
        top=100,
    )

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - INDEXED REVIEWS")
    print("=" * 60)

    count = 0

    for document in results:

        count += 1

        print(f"\nReview {count}")
        print("-" * 60)

        print("ID:", document["id"])

        print(
            "Sentiment:",
            document["sentiment"]
        )

        print(
            "Hash:",
            document["review_hash"]
        )

        print(
            "Review:",
            document["redacted_text"]
        )

    print("\n" + "=" * 60)
    print("TOTAL DOCUMENTS:", count)
    print("=" * 60)