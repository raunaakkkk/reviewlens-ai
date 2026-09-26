from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    embedding = embedding_model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


if __name__ == "__main__":
    sample_text = (
        "The product works well, but delivery was late "
        "and customer support did not respond."
    )

    vector = generate_embedding(sample_text)

    print("Embedding model:", MODEL_NAME)
    print("Embedding dimension:", len(vector))
    print("First 5 values:", vector[:5])