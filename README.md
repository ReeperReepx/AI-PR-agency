# Editorial PR Matchmaking Platform

A journalist-first PR matchmaking platform that only connects companies and journalists when there is a *credible editorial reason* to do so.

## Principles

- **Journalist-First**: Reduce volume, increase relevance, protect trust
- **Explainability**: Every match must answer "why did this happen?"
- **Deterministic Before Probabilistic**: Rules before embeddings, embeddings before LLMs
- **Truth in Structured Data**: AI outputs are derived, never authoritative

## Current Phase

**Phase 1: Core Platform & Identity** (Complete)

- User registration and authentication
- Three user types: Journalist, Company, Admin
- JWT-based authentication
- Basic authorization (admin-only endpoints)

## Project Structure

```
src/
├── core/           # Shared infrastructure
│   ├── config.py   # Application settings
│   ├── database.py # Database connection
│   └── security.py # Password hashing, JWT
├── users/          # User management
│   ├── models.py   # User SQLAlchemy model
│   ├── schemas.py  # Pydantic validation
│   ├── router.py   # User endpoints
│   └── service.py  # User business logic
├── auth/           # Authentication
│   ├── schemas.py  # Auth request/response schemas
│   ├── router.py   # Auth endpoints
│   └── service.py  # Auth logic
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

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | /auth/register | Register a new user | No |
| POST | /auth/login | Get access token | No |
| GET | /users/me | Get current user | Yes |
| GET | /users/{id} | Get user by ID | Yes (self or admin) |
| GET | /users/ | List all users | Yes (admin only) |
| GET | /health | Health check | No |

## Roadmap

1. ~~Core platform & identity~~ (Phase 1 - Complete)
2. Structured data capture (Phase 2)
3. Deterministic matchmaking (Phase 3)
4. Embedding-based discovery (Phase 4)
5. LLM-assisted reasoning (Phase 5)
6. Continuous refinement (Phase 6)
