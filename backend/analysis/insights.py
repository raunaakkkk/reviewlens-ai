from backend.rag.retrieve import retrieve_reviews
from backend.agent.qwen import generate_response


def generate_insights(
    query: str = "What are the main themes and complaints in these customer reviews?",
    top_k: int = 10,
) -> dict:
    """
    Generate structured review insights using:
        Azure AI Search
            ↓
        Vector retrieval
            ↓
        Qwen3 8B

    Returns:
        - themes
        - complaints
        - summary
        - evidence
    """

    # ---------------------------------------------------------
    # 1. Retrieve relevant reviews
    # ---------------------------------------------------------

    reviews = retrieve_reviews(
        query=query,
        top_k=top_k,
    )

    if not reviews:
        return {
            "status": "no_data",
            "themes": [],
            "complaints": [],
            "summary": "No relevant reviews were found.",
            "evidence": [],
        }

    # ---------------------------------------------------------
    # 2. Build evidence context
    # ---------------------------------------------------------

    evidence_parts = []

    for index, review in enumerate(reviews, start=1):

        evidence_parts.append(
            f"""
Evidence {index}

Review ID:
{review["id"]}

Review:
{review["redacted_text"]}

Sentiment:
{review["sentiment"]}
"""
        )

    evidence = "\n".join(evidence_parts)

    # ---------------------------------------------------------
    # 3. Ask Qwen3 8B for structured insights
    # ---------------------------------------------------------

    prompt = f"""
You are ReviewLens AI, a customer review intelligence engine.

Analyze the customer review evidence below.

USER REQUEST:
{query}

REVIEW EVIDENCE:
{evidence}

Return the result using EXACTLY this structure:

THEMES:
- theme 1
- theme 2
- theme 3

COMPLAINTS:
- complaint 1
- complaint 2
- complaint 3

SUMMARY:
Write a short 2-4 sentence summary.

EVIDENCE:
- Evidence 1: explain which theme or complaint it supports.
- Evidence 2: explain which theme or complaint it supports.
- Evidence 3: explain which theme or complaint it supports.

Rules:
- Use ONLY the provided review evidence.
- Do not invent facts.
- Do not invent customer opinions.
- Keep themes and complaints concise.
- If there are fewer than three valid themes or complaints, return only those that are supported.
"""

    answer = generate_response(prompt)

    # ---------------------------------------------------------
    # 4. Return structured result
    # ---------------------------------------------------------

    return {
        "status": "success",
        "query": query,
        "answer": answer,
        "retrieved_reviews": len(reviews),
        "evidence": reviews,
    }


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - REVIEW INSIGHTS")
    print("=" * 60)

    result = generate_insights()

    print("\nSTATUS:")
    print(result["status"])

    print("\nQWEN3 INSIGHTS:")
    print(result.get("answer"))

    print("\nREVIEWS USED AS EVIDENCE:")
    print("-" * 60)

    for index, review in enumerate(
        result.get("evidence", []),
        start=1,
    ):

        print(f"\nEvidence {index}")

        print(
            "Document ID:",
            review["id"]
        )

        print(
            "Sentiment:",
            review["sentiment"]
        )

        print(
            "Review:",
            review["redacted_text"]
        )

    print("\n" + "=" * 60)