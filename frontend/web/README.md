# SentinelStream Web (React)

User-friendly, secure frontend for the SentinelStream FastAPI backend.

## Features
- Sign in / Sign up (`/api/v1/auth/token`, `/api/v1/auth/register`)
- Protected dashboard (JWT auth)
- Dashboard stats (`/api/v1/dashboard/stats`)
- Recent transactions (`/api/v1/transactions/`)
- Submit transaction with `Idempotency-Key`

## Run (dev)

### Prerequisites
- Node.js **with a package manager** (npm/pnpm/yarn).  
  On this machine, `node` exists but `npm` was not found—install Node.js from the official installer to get `npm`.

### Start backend
From repo root:

```bash
docker-compose up --build -d
docker-compose exec fastapi alembic upgrade head
docker-compose exec fastapi python scripts/seed_data.py
```

### Start web
From `frontend/web`:

```bash
npm install
npm run dev
```

Open `http://localhost:3000`.

## Auth + security notes
- JWT is stored in **sessionStorage** (clears on browser close).  
- Requests use `Authorization: Bearer <token>`.
- Transaction submits include `Idempotency-Key` via `crypto.randomUUID()`.

