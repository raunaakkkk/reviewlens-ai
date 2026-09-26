import json
import re
from typing import Any

from backend.analysis.insights import generate_insights


def extract_section(
    text: str,
    section_name: str,
    next_sections: list[str],
) -> list[str]:
    """
    Extract bullet points from a Qwen-generated section.
    """

    next_pattern = "|".join(
        re.escape(section)
        for section in next_sections
    )

    pattern = (
        rf"{re.escape(section_name)}:\s*"
        rf"(.*?)(?=\n(?:{next_pattern}):|\Z)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if not match:
        return []

    section_text = match.group(1)

    items = []

    for line in section_text.splitlines():

        line = line.strip()

        if line.startswith("-"):
            item = line[1:].strip()

            if item:
                items.append(item)

    return items


def build_evidence_links(
    insight_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert ReviewLens insights into structured evidence.
    """

    answer = insight_result.get("answer", "")

    reviews = insight_result.get(
        "evidence",
        [],
    )

    if not answer:
        raise ValueError(
            "Insight result does not contain an answer."
        )

    themes = extract_section(
        answer,
        "THEMES",
        [
            "COMPLAINTS",
            "SUMMARY",
            "EVIDENCE",
        ],
    )

    complaints = extract_section(
        answer,
        "COMPLAINTS",
        [
            "SUMMARY",
            "EVIDENCE",
        ],
    )

    evidence = []

    for review in reviews:

        evidence.append(
            {
                "document_id": review["id"],
                "review_hash": review.get(
                    "review_hash"
                ),
                "sentiment": review["sentiment"],
                "review_text": review["redacted_text"],
                "search_score": review.get(
                    "score"
                ),
            }
        )

    return {
        "themes": themes,
        "complaints": complaints,
        "summary": answer,
        "evidence": evidence,
    }


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("REVIEWLENS AI - EVIDENCE LINKING")
    print("=" * 60)

    result = generate_insights(
        query=(
            "What are the main themes and complaints "
            "in these customer reviews?"
        ),
        top_k=4,
    )

    evidence_result = build_evidence_links(result)

    print("\nTHEMES:")

    for theme in evidence_result["themes"]:
        print(f"- {theme}")

    print("\nCOMPLAINTS:")

    for complaint in evidence_result["complaints"]:
        print(f"- {complaint}")

    print("\nEVIDENCE:")

    for index, item in enumerate(
        evidence_result["evidence"],
        start=1,
    ):

        print(f"\nEvidence {index}")

        print(
            "Document ID:",
            item["document_id"],
        )

        print(
            "Review Hash:",
            item["review_hash"],
        )

        print(
            "Sentiment:",
            item["sentiment"],
        )

        print(
            "Search Score:",
            item["search_score"],
        )

        print(
            "Review:",
            item["review_text"],
        )

    print("\n" + "=" * 60)
    print("STRUCTURED EVIDENCE JSON")
    print("=" * 60)

    print(
        json.dumps(
            evidence_result,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("=" * 60)