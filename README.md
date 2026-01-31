# Editorial PR Matchmaking Platform

A journalist-first PR matchmaking platform that only connects companies and journalists when there is a *credible editorial reason* to do so.

## Principles

- **Journalist-First**: Reduce volume, increase relevance, protect trust
- **Explainability**: Every match must answer "why did this happen?"
- **Deterministic Before Probabilistic**: Rules before embeddings, embeddings before LLMs
- **Truth in Structured Data**: AI outputs are derived, never authoritative

## Current Phase

**Phase 3: Deterministic Matchmaking** (Complete)

- Topic-based matching: companies find journalists with overlapping topics
- Hard rules: only journalists accepting pitches, only active companies
- Explainable results: every match includes why it exists
- Bidirectional: companies search journalists, journalists search companies

## Project Structure

```
src/
├── core/           # Shared infrastructure
├── auth/           # Authentication
├── users/          # User management
├── topics/         # Shared taxonomy
├── journalists/    # Journalist profiles
├── companies/      # Company profiles
├── matching/       # Deterministic matchmaking
│   ├── rules.py    # Pure matching functions
│   ├── schemas.py  # Match result schemas
│   ├── router.py   # Match endpoints
│   └── service.py  # Match orchestration
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

### Users
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /users/me | Get current user | Yes |
| GET | /users/{id} | Get user by ID | Yes (self/admin) |
| GET | /users/ | List all users | Admin |

### Topics
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /topics/ | List all topics | No |
| POST | /topics/ | Create topic | Admin |

### Journalist Profiles
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /journalists/me | Get own profile | Journalist |
| POST | /journalists/me | Create profile | Journalist |
| PUT | /journalists/me | Update profile | Journalist |
| GET | /journalists/{id} | View public profile | Any user |

### Company Profiles
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /companies/me | Get own profile | Company |
| POST | /companies/me | Create profile | Company |
| PUT | /companies/me | Update profile | Company |
| GET | /companies/{id} | View public profile | Any user |

### Matching
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /matches/journalists | Find matching journalists | Company |
| GET | /matches/companies | Find matching companies | Journalist |

### Health
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /health | Health check | No |

## Matching Logic

Matches are **deterministic** and **explainable**:

```
Company requests matches
        │
        ▼
┌─────────────────────────┐
│ 1. Company has topics?  │ → No profile/topics = helpful error
└─────────────────────────┘
        │ Yes
        ▼
┌─────────────────────────┐
│ 2. Find journalists     │
│    with topic overlap   │
│    AND accepting pitches│
└─────────────────────────┘
        │
        ▼
┌─────────────────────────┐
│ 3. Return with reason:  │
│    "Jane at TechNews    │
│    covers AI, which     │
│    aligns with Acme's   │
│    expertise."          │
└─────────────────────────┘
```

## Roadmap

1. ~~Core platform & identity~~ (Phase 1 - Complete)
2. ~~Structured data capture~~ (Phase 2 - Complete)
3. ~~Deterministic matchmaking~~ (Phase 3 - Complete)
4. Embedding-based discovery (Phase 4)
5. LLM-assisted reasoning (Phase 5)
6. Continuous refinement (Phase 6)
