# Editorial PR Matchmaking Platform

A journalist-first PR matchmaking platform that only connects companies and journalists when there is a *credible editorial reason* to do so.

## Principles

- **Journalist-First**: Reduce volume, increase relevance, protect trust
- **Explainability**: Every match must answer "why did this happen?"
- **Deterministic Before Probabilistic**: Rules before embeddings, embeddings before LLMs
- **Truth in Structured Data**: AI outputs are derived, never authoritative

## Current Phase

**Phase 4: Embedding-based Discovery** (Complete)

- Semantic similarity matching using sentence-transformers
- Profile embeddings auto-generated on create/update
- New `/matches/similar/*` endpoints for similarity search
- Similarity scores in match results
- Graceful fallback when model unavailable

## Project Structure

```
src/
├── core/           # Shared infrastructure
├── auth/           # Authentication
├── users/          # User management
├── topics/         # Shared taxonomy
├── journalists/    # Journalist profiles
├── companies/      # Company profiles
├── matching/       # Deterministic + similarity matching
├── embeddings/     # Embedding generation & storage
│   ├── generator.py  # sentence-transformers integration
│   ├── models.py     # ProfileEmbedding storage
│   └── service.py    # Embedding CRUD & similarity search
└── main.py         # FastAPI application
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.main:app --reload

# Run tests
pytest tests/ -v
```

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /auth/register | Register a new user | No |
| POST | /auth/login | Get access token | No |

### Matching (Deterministic)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /matches/journalists | Topic-based journalist matches | Company |
| GET | /matches/companies | Topic-based company matches | Journalist |

### Matching (Similarity)
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /matches/similar/journalists | Semantic similarity matches | Company |
| GET | /matches/similar/companies | Semantic similarity matches | Journalist |

### Profiles
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET/POST/PUT | /journalists/me | Journalist profile management | Journalist |
| GET/POST/PUT | /companies/me | Company profile management | Company |
| GET | /journalists/{id} | View journalist public profile | Any user |
| GET | /companies/{id} | View company public profile | Any user |

### Topics & Users
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /topics/ | List all topics | No |
| POST | /topics/ | Create topic | Admin |
| GET | /users/me | Get current user | Yes |
| GET | /users/ | List all users | Admin |

## Matching Philosophy

```
┌─────────────────────────────────────────────────────┐
│  Phase 3: Deterministic Matching                    │
│  - Exact topic overlap                              │
│  - Hard rules (accepting pitches, active)           │
│  - 100% explainable                                 │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Phase 4: Similarity Matching                       │
│  - Semantic similarity via embeddings               │
│  - Discovers related content beyond exact matches   │
│  - Similarity scores for ranking                    │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────┐
│  Phase 5: LLM-Assisted (Coming)                     │
│  - AI advises, never decides                        │
│  - Human-readable explanations                      │
│  - Risk flagging                                    │
└─────────────────────────────────────────────────────┘
```

## Roadmap

1. ~~Core platform & identity~~ (Phase 1 - Complete)
2. ~~Structured data capture~~ (Phase 2 - Complete)
3. ~~Deterministic matchmaking~~ (Phase 3 - Complete)
4. ~~Embedding-based discovery~~ (Phase 4 - Complete)
5. LLM-assisted reasoning (Phase 5)
6. Continuous refinement (Phase 6)
