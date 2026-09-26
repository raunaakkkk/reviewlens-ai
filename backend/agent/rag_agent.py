from backend.rag.retrieve import retrieve_reviews
from backend.agent.qwen import generate_response


def answer_question(
    question: str,
    top_k: int = 5,
) -> dict:

    # 1. Retrieve relevant reviews
    reviews = retrieve_reviews(
        query=question,
        top_k=top_k,
    )

    if not reviews:
        return {
            "question": question,
            "answer": "No relevant reviews were found.",
            "sources": [],
        }

    # 2. Build evidence context
    evidence_parts = []

    for i, review in enumerate(reviews, start=1):
        evidence_parts.append(
            f"""
Review {i}:
{review["redacted_text"]}

Sentiment: {review["sentiment"]}
"""
        )

    evidence = "\n".join(evidence_parts)

    # 3. Send retrieved evidence to Qwen3
    prompt = f"""
You are ReviewLens AI, a customer review analysis assistant.

Answer the user's question using ONLY the review evidence provided below.

User question:
{question}

Review evidence:
{evidence}

Instructions:
- Do not invent information.
- Base your answer on the provided reviews.
- Mention important complaints or patterns.
- Keep the answer concise.
- If the evidence is insufficient, say so.

Answer:
"""

    answer = generate_response(prompt)

    return {
        "question": question,
        "answer": answer,
        "sources": reviews,
    }


if __name__ == "__main__":
    question = (
        "What are customers complaining about "
        "regarding delivery and customer support?"
    )

    result = answer_question(question)

    print("\nQUESTION:")
    print(result["question"])

    print("\nQWEN3 ANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for source in result["sources"]:
        print(
            f'- {source["sentiment"]}: '
            f'{source["redacted_text"]}'
        )