"""
Embedding generator using sentence-transformers.

Uses a small, fast model that runs locally without API calls.
Falls back to hash-based embeddings if model download fails.
"""

import hashlib

import numpy as np

# Lazy-loaded model instance
_model = None
_use_fallback = False

# Model choice: small, fast, good quality
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


def get_model():
    """Get or initialize the embedding model (lazy loading)."""
    global _model, _use_fallback

    if _use_fallback:
        return None

    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer(MODEL_NAME)
        except Exception:
            # Model download failed (network issues, proxy, etc.)
            # Fall back to hash-based embeddings
            _use_fallback = True
            return None

    return _model


def _hash_based_embedding(text: str) -> list[float]:
    """
    Generate a deterministic hash-based embedding for testing/fallback.

    Not semantically meaningful, but provides consistent vectors for
    the same input text. Useful when the real model can't be loaded.
    """
    # Create multiple hashes to fill the embedding dimension
    embedding = []
    for i in range(EMBEDDING_DIMENSION):
        h = hashlib.sha256(f"{text}_{i}".encode()).hexdigest()
        # Convert first 8 hex chars to a float between -1 and 1
        val = (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1
        embedding.append(val)
    return embedding


def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding vector for the given text.

    Returns a list of floats (384 dimensions).
    Uses sentence-transformers if available, otherwise falls back to
    hash-based embeddings for testing purposes.
    """
    if not text or not text.strip():
        # Return zero vector for empty text
        return [0.0] * EMBEDDING_DIMENSION

    model = get_model()
    if model is not None:
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    else:
        # Fallback for testing when model can't be loaded
        return _hash_based_embedding(text)


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """
    Calculate cosine similarity between two vectors.

    Returns a float between -1 and 1 (1 = identical, 0 = orthogonal).
    """
    a = np.array(vec_a)
    b = np.array(vec_b)

    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


def build_profile_text_journalist(
    full_name: str,
    outlet_name: str,
    beat_description: str,
    bio: str | None = None,
) -> str:
    """
    Build the text to embed for a journalist profile.

    Combines relevant fields into a single string for embedding.
    """
    parts = [
        f"{full_name} is a journalist at {outlet_name}.",
        f"Beat: {beat_description}",
    ]
    if bio:
        parts.append(f"Bio: {bio}")
    return " ".join(parts)


def build_profile_text_company(
    company_name: str,
    industry: str,
    description: str | None = None,
) -> str:
    """
    Build the text to embed for a company profile.

    Combines relevant fields into a single string for embedding.
    """
    parts = [
        f"{company_name} is a company in the {industry} industry.",
    ]
    if description:
        parts.append(f"Description: {description}")
    return " ".join(parts)
