#!/usr/bin/env bash
# Run institutional digest for OpenClaw to forward to Telegram.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
[[ -f .env ]] && set -a && source .env && set +a
export API_BASE="${API_BASE:-http://127.0.0.1:8000}"
export PYTHONPATH="${ROOT}/apps/api:${ROOT}"
exec python3 "${ROOT}/scripts/telegram_institutional_digest.py" "$@"
