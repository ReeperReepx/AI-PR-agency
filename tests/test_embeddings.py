"""
Tests for embedding-based similarity matching.

Tests cover embedding generation, storage, and similarity search.
"""

import pytest


class TestEmbeddingGeneration:
    """Tests for embedding generator functions."""

    def test_generate_embedding_returns_vector(self):
        """Embedding generation returns a list of floats."""
        from src.embeddings.generator import EMBEDDING_DIMENSION, generate_embedding

        text = "This is a test sentence about technology and AI."
        embedding = generate_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) == EMBEDDING_DIMENSION
        assert all(isinstance(x, float) for x in embedding)

    def test_empty_text_returns_zero_vector(self):
        """Empty text returns a zero vector."""
        from src.embeddings.generator import EMBEDDING_DIMENSION, generate_embedding

        embedding = generate_embedding("")
        assert len(embedding) == EMBEDDING_DIMENSION
        assert all(x == 0.0 for x in embedding)

    def test_cosine_similarity_identical_vectors(self):
        """Identical vectors have similarity of 1.0."""
        from src.embeddings.generator import cosine_similarity

        vec = [1.0, 2.0, 3.0]
        similarity = cosine_similarity(vec, vec)
        assert abs(similarity - 1.0) < 0.0001

    def test_cosine_similarity_orthogonal_vectors(self):
        """Orthogonal vectors have similarity of 0.0."""
        from src.embeddings.generator import cosine_similarity

        vec_a = [1.0, 0.0, 0.0]
        vec_b = [0.0, 1.0, 0.0]
        similarity = cosine_similarity(vec_a, vec_b)
        assert abs(similarity) < 0.0001


class TestEmbeddingStorage:
    """Tests for embedding storage and retrieval."""

    def test_journalist_embedding_created_on_profile_create(
        self, client, journalist_user, db_session
    ):
        """Embedding is created when journalist creates profile."""
        from src.embeddings.models import ProfileEmbedding, ProfileType

        # Create profile
        topics = client.get("/topics/").json()
        topic_id = topics[0]["id"]

        response = client.post(
            "/journalists/me",
            json={
                "full_name": "Embedding Test Journalist",
                "outlet_name": "Test Outlet",
                "outlet_type": "online",
                "beat_description": "I cover artificial intelligence and machine learning startups.",
                "topic_ids": [topic_id],
            },
            headers={"Authorization": f"Bearer {journalist_user['token']}"},
        )
        assert response.status_code == 201
        profile_id = response.json()["id"]

        # Check embedding was created
        embedding = (
            db_session.query(ProfileEmbedding)
            .filter(
                ProfileEmbedding.profile_type == ProfileType.journalist,
                ProfileEmbedding.profile_id == profile_id,
            )
            .first()
        )
        assert embedding is not None
        assert len(embedding.embedding) > 0

    def test_company_embedding_created_on_profile_create(
        self, client, company_user, db_session
    ):
        """Embedding is created when company creates profile."""
        from src.embeddings.models import ProfileEmbedding, ProfileType

        topics = client.get("/topics/").json()
        topic_id = topics[0]["id"]

        response = client.post(
            "/companies/me",
            json={
                "company_name": "Embedding Test Company",
                "industry": "Technology",
                "company_size": "startup",
                "description": "We build AI-powered analytics tools for businesses.",
                "topic_ids": [topic_id],
            },
            headers={"Authorization": f"Bearer {company_user['token']}"},
        )
        assert response.status_code == 201
        profile_id = response.json()["id"]

        embedding = (
            db_session.query(ProfileEmbedding)
            .filter(
                ProfileEmbedding.profile_type == ProfileType.company,
                ProfileEmbedding.profile_id == profile_id,
            )
            .first()
        )
        assert embedding is not None
        assert len(embedding.embedding) > 0


class TestSimilaritySearch:
    """Tests for similarity-based matching endpoints."""

    def test_similar_journalists_endpoint(
        self, client, company_with_profile, journalist_with_profile
    ):
        """Company can find similar journalists."""
        response = client.get(
            "/matches/similar/journalists",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert "total" in data

    def test_similar_companies_endpoint(
        self, client, journalist_with_profile, company_with_profile
    ):
        """Journalist can find similar companies."""
        response = client.get(
            "/matches/similar/companies",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "matches" in data
        assert "total" in data

    def test_similar_journalists_requires_company(self, client, journalist_with_profile):
        """Only companies can search for similar journalists."""
        response = client.get(
            "/matches/similar/journalists",
            headers={"Authorization": f"Bearer {journalist_with_profile['token']}"},
        )
        assert response.status_code == 403

    def test_similar_companies_requires_journalist(self, client, company_with_profile):
        """Only journalists can search for similar companies."""
        response = client.get(
            "/matches/similar/companies",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 403

    def test_similar_match_includes_score_and_reason(
        self, client, company_with_profile, journalist_with_profile
    ):
        """Similarity matches include score and reason."""
        response = client.get(
            "/matches/similar/journalists?min_similarity=0.0",
            headers={"Authorization": f"Bearer {company_with_profile['token']}"},
        )
        assert response.status_code == 200
        data = response.json()

        if data["total"] > 0:
            match = data["matches"][0]
            assert "similarity_score" in match
            assert "match_reason" in match
            assert 0.0 <= match["similarity_score"] <= 1.0


class TestSimilarityRelevance:
    """Tests that similarity search returns relevant results."""

    def test_same_text_has_high_similarity(self):
        """
        Same text produces identical embeddings with similarity of 1.0.

        This test works with both real embeddings and hash-based fallback.
        """
        from src.embeddings.generator import cosine_similarity, generate_embedding

        text = "artificial intelligence and machine learning"
        emb1 = generate_embedding(text)
        emb2 = generate_embedding(text)

        similarity = cosine_similarity(emb1, emb2)
        assert abs(similarity - 1.0) < 0.0001

    def test_different_text_has_lower_similarity(self):
        """
        Different text produces different embeddings.

        With real embeddings, similar content would be close.
        With hash fallback, any different text will be different.
        """
        from src.embeddings.generator import cosine_similarity, generate_embedding

        text1 = "artificial intelligence and machine learning"
        text2 = "cooking recipes and restaurant reviews"

        emb1 = generate_embedding(text1)
        emb2 = generate_embedding(text2)

        similarity = cosine_similarity(emb1, emb2)
        # Different text should not be identical
        assert similarity < 0.99
