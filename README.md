# 🛡️ SentinelStream

Real-time fraud detection API built with FastAPI, PostgreSQL, Redis, Celery, Scikit-Learn, Docker, and Nginx.

## Architecture

```
Client → Nginx (port 80) → FastAPI (port 8000) → PostgreSQL + Redis
                                ↓
                          Celery Worker → Webhook delivery
                                ↓
                          ML Model (Isolation Forest)
```

## Tech Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI + Uvicorn |
| Database | PostgreSQL 16 + SQLAlchemy (async) |
| Cache / Queue | Redis 7 |
| Task Queue | Celery |
| ML Model | Scikit-Learn (Isolation Forest) |
| Auth | JWT (python-jose) + bcrypt |
| Containers | Docker + Docker Compose |
| Reverse Proxy | Nginx |
| Testing | PyTest + Locust |

## Quick Start

### Prerequisites
- Docker Desktop
- Python 3.11+
- Git

### Local Development

```bash
# Clone and setup
git clone <repo-url>
cd sentinelstream
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Start infrastructure
docker run -d --name pg -e POSTGRES_PASSWORD=password123 -e POSTGRES_DB=sentinelstream -p 5432:5432 postgres:16-alpine
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Run migrations and seed data
alembic upgrade head
python scripts/seed_data.py

# Train ML model
python ml/generate_training_data.py
python ml/train_model.py

# Start server
uvicorn app.main:app --reload
```

### Docker Compose (Full Stack)

```bash
docker-compose up --build
docker-compose exec fastapi alembic upgrade head
docker-compose exec fastapi python scripts/seed_data.py
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/token` | Login, get JWT |
| POST | `/api/v1/transactions/` | Submit transaction (requires JWT + Idempotency-Key) |
| GET | `/api/v1/transactions/{id}` | Get transaction by ID |
| GET | `/api/v1/transactions/` | List user transactions |
| GET | `/api/v1/rules/` | List fraud rules |
| POST | `/api/v1/rules/` | Create fraud rule (admin only) |
| GET | `/api/v1/dashboard/stats` | Dashboard statistics |

## Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=term-missing

# Load test
locust -f locustfile.py --host=http://localhost:8000
```

## Project Structure

```
sentinelstream/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Security, dependencies, exceptions
│   ├── db/crud/         # Database CRUD operations
│   ├── middleware/       # Idempotency, rate limiting
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic (fraud engine, ML, rules)
│   ├── workers/         # Celery tasks
│   ├── utils/           # Redis client
│   ├── config.py        # Settings
│   └── main.py          # FastAPI app
├── ml/                  # ML training scripts and model
├── tests/               # Test suite
├── docker/              # Dockerfile + Nginx config
├── scripts/             # Seed data
├── docker-compose.yml   # Full stack orchestration
└── locustfile.py        # Load testing
```

