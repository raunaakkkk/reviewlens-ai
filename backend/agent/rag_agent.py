import re

from backend.rag.retrieve import retrieve_reviews
from backend.agent.qwen import generate_response


def clean_ai_response(text: str) -> str:
    """
    Clean formatting artifacts returned by Qwen3.
    """

    if not text:
        return ""

    # HTML space entities
    text = text.replace("&#x20;", " ")
    text = text.replace("&#32;", " ")
    text = text.replace("&nbsp;", " ")

    # Escaped Markdown
    text = text.replace(r"\*", "*")
    text = text.replace(r"\.", ".")
    text = text.replace(r"\_", "_")
    text = text.replace(r"\#", "#")
    text = text.replace(r"\-", "-")
    text = text.replace(r"\`", "`")

    # Remove Markdown bold
    text = text.replace("**", "")

    # Remove Markdown italic
    text = re.sub(
        r"\*([^*\n]+)\*",
        r"\1",
        text,
    )

    # Remove code ticks
    text = text.replace("`", "")

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove trailing spaces
    text = re.sub(
        r"[ \t]+\n",
        "\n",
        text,
    )

    # Remove excessive blank lines
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def answer_question(
    question: str,
    top_k: int = 5,
) -> dict:

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

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

    evidence_parts = []

    for index, review in enumerate(
        reviews,
        start=1,
    ):

        evidence_parts.append(
            f"""
Review {index}:

{review["redacted_text"]}

Sentiment:
{review["sentiment"]}
"""
        )

    evidence = "\n".join(
        evidence_parts
    )

    prompt = f"""
You are ReviewLens AI, a customer review analysis assistant.

Answer the user's question using ONLY the review evidence provided below.

User question:
{question}

Review evidence:
{evidence}

Instructions:

- Use ONLY the provided review evidence.
- Do not invent information.
- Do not invent customer opinions.
- Mention the important complaints or patterns.
- Keep the answer concise.
- If the evidence is insufficient, say so.
- Do NOT use Markdown bold.
- Do NOT use asterisks.
- Do NOT use HTML entities.
- Do NOT use escaped characters.
- Do NOT include a title such as "ReviewLens AI".
- Return plain text only.

Answer:
"""

    raw_answer = generate_response(prompt)

    # Clean Qwen output before returning it
    answer = clean_ai_response(
        raw_answer
    )

    return {
        "question": question,
        "answer": answer,
        "sources": reviews,
    }