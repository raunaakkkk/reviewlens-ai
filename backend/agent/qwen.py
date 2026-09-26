import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:8b"


def generate_response(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        timeout=600,
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]


def analyze_review(review_text: str) -> str:
    prompt = f"""
You are the ReviewLens AI review analysis engine.

Analyze the following customer review.

Review:
{review_text}

Return:
1. Overall sentiment
2. Main complaint
3. Key issue
4. Short summary

Keep the answer concise and factual.
"""

    return generate_response(prompt)