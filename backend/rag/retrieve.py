from azure.search.documents.models import VectorizedQuery

from backend.rag.embeddings import generate_embedding
from backend.rag.search import get_search_client


def retrieve_reviews(
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieve the most relevant reviews from Azure AI Search
    using vector similarity.

    Pipeline:
        User query
            ↓
        all-MiniLM-L6-v2
            ↓
        384-dimensional embedding
            ↓
        Azure AI Search
            ↓
        Relevant reviews
    """

    # ---------------------------------------------------------
    # 1. Validate query
    # ---------------------------------------------------------

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    # ---------------------------------------------------------
    # 2. Generate query embedding
    # ---------------------------------------------------------

    query_embedding = generate_embedding(query)

    # ---------------------------------------------------------
    # 3. Create vector search query
    # ---------------------------------------------------------

    vector_query = VectorizedQuery(
        vector=query_embedding,
        k_nearest_neighbors=top_k,
        fields="embedding",
    )

    # ---------------------------------------------------------
    # 4. Get Azure AI Search client
    # ---------------------------------------------------------

    search_client = get_search_client()

    # ---------------------------------------------------------
    # 5. Search Azure AI Search
    # ---------------------------------------------------------

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=[
            "id",
            "review_text",
            "redacted_text",
            "sentiment",
            "positive_score",
            "neutral_score",
            "negative_score",
            "review_hash",
        ],
        top=top_k,
    )

    # ---------------------------------------------------------
    # 6. Convert results into Python dictionaries
    # ---------------------------------------------------------

    retrieved_reviews = []

    for result in results:

        retrieved_reviews.append(
            {
                "id": result["id"],

                "review_text": result["review_text"],

                "redacted_text": result["redacted_text"],

                "sentiment": result["sentiment"],

                "positive_score": result["positive_score"],

                "neutral_score": result["neutral_score"],

                "negative_score": result["negative_score"],

                "review_hash": result.get(
                    "review_hash"
                ),

                "score": result.get(
                    "@search.score"
                ),
            }
        )

    return retrieved_reviews


if __name__ == "__main__":

    query = (
        "What are customers complaining about "
        "regarding delivery and customer support?"
    )

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - VECTOR RETRIEVAL TEST")
    print("=" * 60)

    reviews = retrieve_reviews(
        query=query,
        top_k=5,
    )

    print("\nQuery:")
    print(query)

    print("\nRetrieved reviews:")
    print("-" * 60)

    for index, review in enumerate(
        reviews,
        start=1,
    ):

        print(f"\nResult {index}")

        print(
            "Document ID:",
            review["id"],
        )

        print(
            "Score:",
            review["score"],
        )

        print(
            "Sentiment:",
            review["sentiment"],
        )

        print(
            "Review hash:",
            review["review_hash"],
        )

        print(
            "Review:",
            review["redacted_text"],
        )

    print("\n" + "=" * 60)
    print(
        "Total retrieved:",
        len(reviews),
    )
    print("=" * 60)