# Editorial PR Matchmaking Platform

A journalist-first PR matchmaking platform that only connects companies and journalists when there is a *credible editorial reason* to do so.

## Principles

- **Journalist-First**: Reduce volume, increase relevance, protect trust
- **Explainability**: Every match must answer "why did this happen?"
- **Deterministic Before Probabilistic**: Rules before embeddings, embeddings before LLMs
- **Truth in Structured Data**: AI outputs are derived, never authoritative

## Current Phase

**Phase 2: Structured Data Capture** (Complete)

- Shared topic taxonomy (seeded with 27 topics across 5 categories)
- Journalist profiles: beats, outlets, pitch preferences
- Company profiles: industry, size, expertise areas
- Many-to-many topic associations for matching foundation

## Project Structure

```
src/
├── core/           # Shared infrastructure
│   ├── config.py   # Application settings
│   ├── database.py # Database connection
│   └── security.py # Password hashing, JWT
├── auth/           # Authentication
│   ├── schemas.py  # Auth request/response schemas
│   ├── router.py   # Auth endpoints
│   └── service.py  # Auth logic
├── users/          # User management
│   ├── models.py   # User SQLAlchemy model
│   ├── schemas.py  # Pydantic validation
│   ├── router.py   # User endpoints
│   └── service.py  # User business logic
├── topics/         # Shared taxonomy
│   ├── models.py   # Topic model
│   ├── schemas.py  # Topic schemas
│   ├── router.py   # Topic endpoints
│   └── service.py  # Topic logic + seeding
├── journalists/    # Journalist profiles
│   ├── models.py   # JournalistProfile model
│   ├── schemas.py  # Profile schemas
│   ├── router.py   # Profile endpoints
│   └── service.py  # Profile logic
├── companies/      # Company profiles
│   ├── models.py   # CompanyProfile model
│   ├── schemas.py  # Profile schemas
│   ├── router.py   # Profile endpoints
│   └── service.py  # Profile logic
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

### Health
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /health | Health check | No |

## Roadmap

1. ~~Core platform & identity~~ (Phase 1 - Complete)
2. ~~Structured data capture~~ (Phase 2 - Complete)
3. Deterministic matchmaking (Phase 3)
4. Embedding-based discovery (Phase 4)
5. LLM-assisted reasoning (Phase 5)
6. Continuous refinement (Phase 6)
