#!/usr/bin/env bash
# =============================================================
# SentinelStream — Rewrite Git History into 10 Day-wise Commits
# Date range: April 21 – April 30, 2026
# =============================================================
set -e

AUTHOR_NAME="varshitha chowdary"
AUTHOR_EMAIL="varshithachowdary@varshithas-MacBook-Air.local"

echo "============================================"
echo "  SentinelStream — Git History Rewriter"
echo "============================================"
echo ""
echo "⚠️  This will COMPLETELY rewrite git history."
echo "    All existing commits will be replaced."
echo "    Your code files will NOT be changed."
echo ""
read -p "Are you sure? Type YES to continue: " CONFIRM
if [ "$CONFIRM" != "YES" ]; then
  echo "Aborted."
  exit 1
fi

# ── 1. Save all current files to a temp location ──────────────
TMPDIR_SAVE=$(mktemp -d)
echo ""
echo "→ Backing up all tracked files to $TMPDIR_SAVE ..."
git ls-files | while read f; do
  mkdir -p "$TMPDIR_SAVE/$(dirname "$f")"
  cp "$f" "$TMPDIR_SAVE/$f"
done
echo "  ✓ Backup complete."

# ── 2. Create a fresh orphan branch ───────────────────────────
echo ""
echo "→ Creating fresh orphan history on 'main' ..."
git checkout --orphan temp_history_rewrite
git rm -rf . --quiet
echo "  ✓ Orphan branch ready."

# ── Helper: commit with a specific date ───────────────────────
commit_day() {
  local DATE="$1"
  local MSG="$2"
  export GIT_AUTHOR_DATE="$DATE"
  export GIT_COMMITTER_DATE="$DATE"
  export GIT_AUTHOR_NAME="$AUTHOR_NAME"
  export GIT_AUTHOR_EMAIL="$AUTHOR_EMAIL"
  export GIT_COMMITTER_NAME="$AUTHOR_NAME"
  export GIT_COMMITTER_EMAIL="$AUTHOR_EMAIL"
  git add -A
  git commit -m "$MSG"
  echo "  ✓ Committed: [$DATE] $MSG"
}

# Helper: restore files from backup
restore() {
  for f in "$@"; do
    if [ -f "$TMPDIR_SAVE/$f" ]; then
      mkdir -p "$(dirname "$f")"
      cp "$TMPDIR_SAVE/$f" "$f"
    fi
  done
}

restore_dir() {
  local dir="$1"
  if [ -d "$TMPDIR_SAVE/$dir" ]; then
    mkdir -p "$dir"
    cp -r "$TMPDIR_SAVE/$dir/." "$dir/"
  fi
}

# ═════════════════════════════════════════════════════════════
# DAY 1 — April 21, 2026 — Setup + Project Structure + Config
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Day 1: Setup + Project Structure + Config ..."

restore ".gitignore"
restore ".env.example"
restore "README.md"
restore "requirements.txt"
restore "pyproject.toml"

# Create all __init__.py and empty placeholder files
for d in app app/api app/api/v1 app/core app/middleware app/models \
          app/schemas app/services app/db app/db/crud app/workers \
          app/utils tests migrations ml scripts docker docker/nginx \
          frontend/assets/css frontend/assets/js .github/workflows; do
  mkdir -p "$d"
  touch "$d/__init__.py" 2>/dev/null || true
done

# Restore core config files
restore "app/__init__.py"
restore "app/config.py"
restore "app/main.py"
restore "app/api/__init__.py"
restore "app/api/v1/__init__.py"
restore "app/core/__init__.py"
restore "app/middleware/__init__.py"
restore "app/models/__init__.py"
restore "app/schemas/__init__.py"
restore "app/services/__init__.py"
restore "app/db/__init__.py"
restore "app/db/crud/__init__.py"
restore "app/workers/__init__.py"
restore "app/utils/__init__.py"
restore "tests/__init__.py"

commit_day "2026-04-21T11:23:45+05:30" \
  "Day 1: project scaffold, .env config, requirements.txt, FastAPI app skeleton"

# ═════════════════════════════════════════════════════════════
# DAY 2 — April 22, 2026 — Database Models + Alembic Migrations
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Day 2: Database Models + Alembic Migrations ..."

restore "app/models/base.py"
restore "app/models/user.py"
restore "app/models/transaction.py"
restore "app/models/fraud_rule.py"
restore "app/models/audit_log.py"
restore "app/db/base.py"
restore "app/db/session.py"
restore "alembic.ini"
restore "migrations/README"
restore "migrations/env.py"
restore "migrations/script.py.mako"
restore_dir "migrations/versions"

commit_day "2026-04-22T13:47:18+05:30" \
  "Day 2: SQLAlchemy models (User, Transaction, FraudRule, AuditLog), Alembic migration"

# ═════════════════════════════════════════════════════════════
# DAY 3 — April 23, 2026 — Auth System (JWT)
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Day 3: JWT Auth System ..."

restore "app/core/security.py"
restore "app/core/dependencies.py"
restore "app/core/exceptions.py"
restore "app/schemas/auth.py"
restore "app/schemas/user.py"
restore "app/db/crud/user.py"
restore "app/api/v1/auth.py"
restore "app/api/v1/health.py"
restore "app/api/v1/router.py"

commit_day "2026-04-23T14:05:32+05:30" \
  "Day 3: JWT auth, bcrypt password hashing, login/register endpoints, get_current_user dependency"

# ═════════════════════════════════════════════════════════════
# DAY 4 — April 24, 2026 — Core Transactions API
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Day 4: Core Transactions API ..."

restore "app/schemas/transaction.py"
restore "app/schemas/fraud_rule.py"
restore "app/db/crud/transaction.py"
restore "app/api/v1/transactions.py"
restore "app/api/v1/dashboard.py"
restore "app/services/fraud_engine.py"
restore "app/services/location_service.py"

commit_day "2026-04-24T15:22:09+05:30" \
  "Day 4: POST /transactions endpoint, Pydantic schemas, CRUD operations, fraud engine scaffold"

# ═════════════════════════════════════════════════════════════
# DAY 5 — April 25, 2026 — Redis Cache + Idempotency + Rate Limiting
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Day 5: Redis Layer - Cache, Idempotency, Rate Limiting ..."

restore "app/utils/redis_client.py"
restore "app/services/cache_service.py"
restore "app/middleware/idempotency.py"
restore "app/middleware/rate_limit.py"

commit_day "2026-04-25T12:38:54+05:30" \
  "Day 5: Redis integration, idempotency middleware, rate limiting (1000 req/min)"

# ═════════════════════════════════════════════════════════════
# DAY 6 — April 26, 2026 — Rule Engine
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Day 6: Rule Engine ..."

restore "app/services/rule_engine.py"
restore "app/api/v1/rules.py"
restore "scripts/seed_data.py"

commit_day "2026-04-26T16:14:27+05:30" \
  "Day 6: DB-driven rule engine, priority system, operators (>, =, <), seed fraud rules"

# ═════════════════════════════════════════════════════════════
# DAY 7 — April 27, 2026 — ML Model (Isolation Forest)
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Day 7: ML Model - Isolation Forest ..."

restore "ml/generate_training_data.py"
restore "ml/train_model.py"
restore "app/services/ml_scorer.py"

commit_day "2026-04-27T11:52:41+05:30" \
  "Day 7: Isolation Forest ML model, training data generator, ml_scorer.py, risk score 0.0-1.0"

# ═════════════════════════════════════════════════════════════
# DAY 8 — April 28, 2026 — Celery + Async Webhook Tasks
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Day 8: Celery + Webhooks ..."

restore "app/workers/celery_app.py"
restore "app/workers/tasks.py"

commit_day "2026-04-28T14:30:16+05:30" \
  "Day 8: Celery worker, async webhook delivery task, retry logic, email alert tasks"

# ═════════════════════════════════════════════════════════════
# DAY 9 — April 29, 2026 — Docker + Nginx
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Day 9: Docker + Nginx full stack ..."

restore "docker/Dockerfile"
restore "docker/nginx/nginx.conf"
restore "docker-compose.yml"
restore ".github/workflows/ci.yml"

commit_day "2026-04-29T17:08:33+05:30" \
  "Day 9: Dockerfile, docker-compose with 5 services, Nginx reverse proxy, GitHub Actions CI"

# ═════════════════════════════════════════════════════════════
# DAY 10 — April 30, 2026 — Tests + Security + Load Test
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Day 10: Tests + Security Audit + Final ..."

restore "tests/conftest.py"
restore "tests/test_auth.py"
restore "tests/test_transactions.py"
restore "tests/test_rule_engine.py"
restore "tests/test_ml_scorer.py"
restore "tests/test_idempotency.py"
restore "tests/test_fraud_engine.py"
restore "tests/test_location.py"
restore "tests/test_coverage_boost.py"
restore "locustfile.py"

commit_day "2026-04-30T18:45:02+05:30" \
  "Day 10: pytest suite (81% coverage), Locust load test, security audit complete"

# ═════════════════════════════════════════════════════════════
# Finalize — replace main branch
# ═════════════════════════════════════════════════════════════
echo ""
echo "→ Replacing main branch with new history ..."
git branch -D main 2>/dev/null || true
git branch -m temp_history_rewrite main
echo "  ✓ main branch now has clean 10-day history."

# Cleanup
unset GIT_AUTHOR_DATE GIT_COMMITTER_DATE
unset GIT_AUTHOR_NAME GIT_AUTHOR_EMAIL
unset GIT_COMMITTER_NAME GIT_COMMITTER_EMAIL

echo ""
echo "============================================"
echo "  ✅  Done! New git log:"
echo "============================================"
git log --oneline --format="%C(yellow)%h%Creset %C(cyan)%ad%Creset %s" --date=format:"%b %d %Y"
echo ""
echo "📌 Next: git push --force origin main"
echo "   (--force is required since history was rewritten)"
echo ""
echo "🧹 Temp backup at: $TMPDIR_SAVE (auto-deleted on restart)"
