"""
Embedding service for generating and querying embeddings.
"""

from sqlalchemy.orm import Session

from src.companies.models import CompanyProfile
from src.embeddings.generator import (
    build_profile_text_company,
    build_profile_text_journalist,
    cosine_similarity,
    generate_embedding,
)
from src.embeddings.models import ProfileEmbedding, ProfileType
from src.journalists.models import JournalistProfile


def get_embedding(
    db: Session, profile_type: ProfileType, profile_id: str
) -> ProfileEmbedding | None:
    """Get stored embedding for a profile."""
    return (
        db.query(ProfileEmbedding)
        .filter(
            ProfileEmbedding.profile_type == profile_type,
            ProfileEmbedding.profile_id == profile_id,
        )
        .first()
    )


def upsert_journalist_embedding(
    db: Session, journalist: JournalistProfile
) -> ProfileEmbedding:
    """Generate and store embedding for a journalist profile."""
    source_text = build_profile_text_journalist(
        full_name=journalist.full_name,
        outlet_name=journalist.outlet_name,
        beat_description=journalist.beat_description,
        bio=journalist.bio,
    )

    embedding_vector = generate_embedding(source_text)

    existing = get_embedding(db, ProfileType.journalist, journalist.id)

    if existing:
        existing.embedding = embedding_vector
        existing.source_text = source_text
        db.commit()
        db.refresh(existing)
        return existing

    new_embedding = ProfileEmbedding(
        profile_type=ProfileType.journalist,
        profile_id=journalist.id,
        source_text=source_text,
    )
    new_embedding.embedding = embedding_vector
    db.add(new_embedding)
    db.commit()
    db.refresh(new_embedding)
    return new_embedding


def upsert_company_embedding(db: Session, company: CompanyProfile) -> ProfileEmbedding:
    """Generate and store embedding for a company profile."""
    source_text = build_profile_text_company(
        company_name=company.company_name,
        industry=company.industry,
        description=company.description,
    )

    embedding_vector = generate_embedding(source_text)

    existing = get_embedding(db, ProfileType.company, company.id)

    if existing:
        existing.embedding = embedding_vector
        existing.source_text = source_text
        db.commit()
        db.refresh(existing)
        return existing

    new_embedding = ProfileEmbedding(
        profile_type=ProfileType.company,
        profile_id=company.id,
        source_text=source_text,
    )
    new_embedding.embedding = embedding_vector
    db.add(new_embedding)
    db.commit()
    db.refresh(new_embedding)
    return new_embedding


def find_similar_journalists(
    db: Session,
    company_id: str,
    min_similarity: float = 0.3,
    limit: int = 20,
) -> list[tuple[JournalistProfile, float]]:
    """
    Find journalists with similar embeddings to a company.

    Returns list of (journalist, similarity_score) tuples, sorted by similarity.
    """
    company_embedding = get_embedding(db, ProfileType.company, company_id)
    if not company_embedding:
        return []

    company_vec = company_embedding.embedding

    # Get all journalist embeddings
    journalist_embeddings = (
        db.query(ProfileEmbedding)
        .filter(ProfileEmbedding.profile_type == ProfileType.journalist)
        .all()
    )

    results = []
    for j_emb in journalist_embeddings:
        similarity = cosine_similarity(company_vec, j_emb.embedding)
        if similarity >= min_similarity:
            journalist = (
                db.query(JournalistProfile)
                .filter(JournalistProfile.id == j_emb.profile_id)
                .first()
            )
            if journalist and journalist.is_accepting_pitches:
                results.append((journalist, similarity))

    # Sort by similarity descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]


def find_similar_companies(
    db: Session,
    journalist_id: str,
    min_similarity: float = 0.3,
    limit: int = 20,
) -> list[tuple[CompanyProfile, float]]:
    """
    Find companies with similar embeddings to a journalist.

    Returns list of (company, similarity_score) tuples, sorted by similarity.
    """
    journalist_embedding = get_embedding(db, ProfileType.journalist, journalist_id)
    if not journalist_embedding:
        return []

    journalist_vec = journalist_embedding.embedding

    # Get all company embeddings
    company_embeddings = (
        db.query(ProfileEmbedding)
        .filter(ProfileEmbedding.profile_type == ProfileType.company)
        .all()
    )

    results = []
    for c_emb in company_embeddings:
        similarity = cosine_similarity(journalist_vec, c_emb.embedding)
        if similarity >= min_similarity:
            company = (
                db.query(CompanyProfile)
                .filter(CompanyProfile.id == c_emb.profile_id)
                .first()
            )
            if company and company.is_active:
                results.append((company, similarity))

    # Sort by similarity descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:limit]
