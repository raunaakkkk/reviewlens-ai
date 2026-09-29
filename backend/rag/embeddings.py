from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

embedding_model = SentenceTransformer(MODEL_NAME)


# =========================================================
# SINGLE TEXT
# Existing API preserved
# =========================================================

def generate_embedding(text: str) -> list[float]:
    """
    Generate a normalized 384-dimensional embedding
    for one text.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    embedding = embedding_model.encode(
        text,
        normalize_embeddings=True,
    )

    return embedding.tolist()


# =========================================================
# BATCH EMBEDDINGS
# =========================================================

def generate_embeddings(
    texts: list[str],
    batch_size: int = 32,
) -> list[list[float]]:
    """
    Generate normalized embeddings for multiple texts.

    The order of returned embeddings matches the
    order of the input texts.
    """

    if not texts:
        return []

    for index, text in enumerate(texts):
        if not text or not text.strip():
            raise ValueError(
                f"Text at index {index} is empty."
            )

    embeddings = embedding_model.encode(
        texts,
        batch_size=batch_size,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    return embeddings.tolist()