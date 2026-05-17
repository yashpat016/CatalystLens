#!/usr/bin/env bash
# Start CatalystLens API + Web locally (no Docker).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f "${ROOT}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT}/.env"
  set +a
fi

export DATABASE_URL="${DATABASE_URL:-sqlite:///${ROOT}/.local/catalystlens.db}"
export FIXTURES_DIR="${FIXTURES_DIR:-${ROOT}/apps/api/app/fixtures}"
export PYTHONPATH="${ROOT}/apps/api:${ROOT}"
export NEXT_PUBLIC_API_BASE_URL="${NEXT_PUBLIC_API_BASE_URL:-http://localhost:8000}"
export API_BASE_URL_INTERNAL="${API_BASE_URL_INTERNAL:-http://127.0.0.1:8000}"

mkdir -p .local

# Python venv
if [[ ! -d apps/api/.venv ]]; then
  python3 -m venv apps/api/.venv
  source apps/api/.venv/bin/activate
  pip install -q --upgrade pip
  pip install -q \
    "fastapi>=0.110" "uvicorn[standard]>=0.27" "sqlalchemy>=2.0" "alembic>=1.13" \
    "pydantic>=2.6" "pydantic-settings>=2.2" "python-dotenv>=1.0" "httpx>=0.27" \
    "structlog>=24.1" "pytest>=8.0" "respx>=0.21" "psycopg[binary]>=3.1"
else
  source apps/api/.venv/bin/activate
fi

echo "==> Bootstrapping DB + fixtures..."
python scripts/bootstrap_local.py

echo "==> Backend tests..."
cd apps/api && PYTHONPATH=. pytest app/tests -q && cd "$ROOT"

echo "==> Installing web dependencies..."
cd apps/web
if [[ ! -d node_modules ]]; then
  npm install --silent
fi

echo "==> Frontend tests..."
npm run test:run

echo "==> Starting API on :8000..."
cd "$ROOT/apps/api"
uvicorn app.main:app --host 127.0.0.1 --port 8000 &
API_PID=$!

echo "==> Starting Web on :3000..."
cd "$ROOT/apps/web"
# Stale .next cache (e.g. after `next build` while dev is running) causes blank/500 pages.
rm -rf .next
npm run dev -- -p 3000 -H 127.0.0.1 &
WEB_PID=$!

cleanup() {
  kill "$API_PID" "$WEB_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "Waiting for services..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/api/health >/dev/null 2>&1; then break; fi
  sleep 1
done
for i in $(seq 1 60); do
  if curl -sf http://localhost:3000 >/dev/null 2>&1; then break; fi
  sleep 1
done

echo ""
echo "==> Smoke tests"
curl -sf http://localhost:8000/api/health | python3 -m json.tool
curl -sf http://localhost:8000/api/tickers/AAPL/summary | python3 -m json.tool | head -20
curl -sf "http://localhost:8000/api/tickers/AAPL/bars?timeframe=1m&limit=2" | python3 -m json.tool | head -30
curl -sf http://localhost:8000/api/tickers/AAPL/fundamentals | python3 -m json.tool | head -40

HTTP_WEB=$(curl -sf -o /dev/null -w "%{http_code}" http://localhost:3000/ticker/AAPL)
echo "Web /ticker/AAPL HTTP status: $HTTP_WEB"

if [[ "$HTTP_WEB" != "200" ]]; then
  echo "FAIL: expected 200 from ticker page"
  exit 1
fi

echo ""
echo "SUCCESS"
echo "  GUI:  http://localhost:3000/ticker/AAPL"
echo "  API:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop."

wait
