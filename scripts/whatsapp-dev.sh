#!/usr/bin/env bash
# MTEJA AI WhatsApp development runner
# Starts Postgres (Docker), the backend and an ngrok tunnel on a static domain,
# so the webhook URL registered in Meta never changes.
#
# Usage:
#   scripts/whatsapp-dev.sh              # Postgres + backend + ngrok (real WhatsApp)
#   scripts/whatsapp-dev.sh --dry-run    # replies are logged, not sent to Meta
#   scripts/whatsapp-dev.sh --no-tunnel  # local only; test with scripts/whatsapp_simulate.py
#
# Settings are read from backend/.env (see backend/.env.example).
# BACKEND_PORT (default 8001) can be overridden from the environment.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/backend/.env"
LOG_DIR="$ROOT/backend/logs"
BACKEND_PORT="${BACKEND_PORT:-8001}"
DB_CONTAINER="mteja-ai-dev-postgres"
DB_VOLUME="mteja-ai_postgres_data"
TUNNEL=1

for arg in "$@"; do
  case "$arg" in
    --dry-run) export WHATSAPP_DRY_RUN=true ;;
    --no-tunnel) TUNNEL=0 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

info() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m!!\033[0m  %s\n' "$*"; }
die()  { printf '\033[1;31mxx\033[0m  %s\n' "$*" >&2; exit 1; }

# Value of KEY from the environment, else from backend/.env; "<...>" placeholders count as unset
env_value() {
  local key="$1" value="${!1:-}"
  if [[ -z "$value" ]]; then
    value="$(grep -E "^${key}=" "$ENV_FILE" | tail -1 | cut -d= -f2- | sed -E "s/^['\"]//; s/['\"]$//")" || true
  fi
  [[ "$value" == "<"* ]] && value=""
  printf '%s' "$value"
}

port_in_use() { ss -ltn "( sport = :$1 )" 2>/dev/null | grep -q LISTEN; }

[[ -f "$ENV_FILE" ]] || die "backend/.env not found. Copy backend/.env.example to backend/.env and fill it in."

# Unfilled "<...>" placeholders must reach the backend as empty, not as literal secrets
for key in META_APP_SECRET WHATSAPP_ACCESS_TOKEN WHATSAPP_PHONE_NUMBER_ID OPENAI_API_KEY; do
  if [[ -z "${!key:-}" ]] && grep -qE "^${key}=<" "$ENV_FILE"; then
    export "$key="
  fi
done

# ------------------------------------------------------------------
# Python
# ------------------------------------------------------------------
PYTHON=""
for candidate in "$ROOT/.venv/bin/python" "$ROOT/backend/.venv/bin/python" "$ROOT/backend/venv/bin/python"; do
  [[ -x "$candidate" ]] && { PYTHON="$candidate"; break; }
done
PYTHON="${PYTHON:-python3}"
"$PYTHON" -c "import uvicorn" 2>/dev/null || die "uvicorn is not installed for $PYTHON. Install the backend dependencies first."

# ------------------------------------------------------------------
# Postgres (only managed here when DATABASE_URL points at localhost)
# ------------------------------------------------------------------
DATABASE_URL="$(env_value DATABASE_URL)"
if [[ "$DATABASE_URL" =~ ^postgresql(\+asyncpg)?://([^:]+):([^@]+)@(localhost|127\.0\.0\.1):([0-9]+)/([^?]+) ]]; then
  DB_USER="${BASH_REMATCH[2]}" DB_PASS="${BASH_REMATCH[3]}" DB_PORT="${BASH_REMATCH[5]}" DB_NAME="${BASH_REMATCH[6]}"

  if [[ "$(docker inspect -f '{{.State.Running}}' "$DB_CONTAINER" 2>/dev/null)" == "true" ]]; then
    info "Postgres already running ($DB_CONTAINER)"
  else
    if docker inspect "$DB_CONTAINER" >/dev/null 2>&1; then
      bound_port="$(docker inspect -f '{{(index (index .HostConfig.PortBindings "5432/tcp") 0).HostPort}}' "$DB_CONTAINER")"
      if [[ "$bound_port" != "$DB_PORT" ]]; then
        info "Recreating $DB_CONTAINER on port $DB_PORT (was $bound_port); data is kept in volume $DB_VOLUME"
        docker rm "$DB_CONTAINER" >/dev/null
      fi
    fi
    port_in_use "$DB_PORT" && die "Port $DB_PORT is used by another program. Pick a free port in DATABASE_URL in backend/.env (e.g. 5440)."
    if docker inspect "$DB_CONTAINER" >/dev/null 2>&1; then
      info "Starting Postgres ($DB_CONTAINER) on port $DB_PORT"
      docker start "$DB_CONTAINER" >/dev/null
    else
      info "Creating Postgres ($DB_CONTAINER) on port $DB_PORT"
      docker run -d --name "$DB_CONTAINER" \
        -e POSTGRES_USER="$DB_USER" -e POSTGRES_PASSWORD="$DB_PASS" -e POSTGRES_DB="$DB_NAME" \
        -p "127.0.0.1:$DB_PORT:5432" -v "$DB_VOLUME:/var/lib/postgresql/data" \
        postgres:16-alpine >/dev/null
    fi
  fi

  for _ in $(seq 1 30); do
    docker exec "$DB_CONTAINER" pg_isready -U "$DB_USER" -d "$DB_NAME" -q 2>/dev/null && break
    sleep 1
  done
  docker exec "$DB_CONTAINER" pg_isready -U "$DB_USER" -d "$DB_NAME" -q || die "Postgres did not become ready"
else
  DB_CONTAINER=""
  warn "DATABASE_URL is not a localhost Postgres; using it as-is"
fi

# ------------------------------------------------------------------
# Backend
# ------------------------------------------------------------------
port_in_use "$BACKEND_PORT" && die "Port $BACKEND_PORT is already in use. Stop that program or run with BACKEND_PORT=<free port>."

if [[ -z "$(env_value OPENAI_API_KEY)" ]]; then
  # chat_service.py builds its OpenAI client at import time and crashes without a key
  warn "OPENAI_API_KEY is not set: using a placeholder so the app can start (no real AI replies)"
  export OPENAI_API_KEY="sk-placeholder-not-real"
fi
[[ -z "$(env_value META_APP_SECRET)" ]] && warn "META_APP_SECRET is not set: webhook signatures are NOT checked"
[[ "${WHATSAPP_DRY_RUN:-}" == "true" ]] && info "Dry-run: WhatsApp replies are logged, not sent"

mkdir -p "$LOG_DIR"
PIDS=()
cleanup() {
  trap - INT TERM EXIT
  info "Stopping..."
  for pid in "${PIDS[@]}"; do kill "$pid" 2>/dev/null || true; done
  wait 2>/dev/null || true
  [[ -n "$DB_CONTAINER" ]] && info "Postgres is still running. Stop it with: docker stop $DB_CONTAINER"
}
trap cleanup INT TERM EXIT

info "Starting backend on http://localhost:$BACKEND_PORT (log: backend/logs/backend.log)"
(cd "$ROOT/backend" && exec "$PYTHON" -m uvicorn app.main:app --reload --port "$BACKEND_PORT") \
  > "$LOG_DIR/backend.log" 2>&1 &
PIDS+=("$!")

for _ in $(seq 1 60); do
  curl -sf "http://localhost:$BACKEND_PORT/health" >/dev/null && break
  kill -0 "${PIDS[0]}" 2>/dev/null || { tail -20 "$LOG_DIR/backend.log"; die "Backend exited during startup"; }
  sleep 1
done
curl -sf "http://localhost:$BACKEND_PORT/health" >/dev/null || die "Backend did not become healthy; see backend/logs/backend.log"

# The webhook path needs an organization id; make sure organization 1 exists on a fresh database
if [[ -n "$DB_CONTAINER" ]]; then
  docker exec "$DB_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -qtAc \
    "INSERT INTO organizations (name, settings, ai_settings) SELECT 'Dev Business', '{}', '{}' WHERE NOT EXISTS (SELECT 1 FROM organizations);" >/dev/null
fi
ORG_ID="${ORG_ID:-1}"
WEBHOOK_PATH="/api/v1/webhooks/whatsapp/$ORG_ID"

# ------------------------------------------------------------------
# ngrok tunnel on a static domain
# ------------------------------------------------------------------
PUBLIC_URL=""
NGROK_DOMAIN="$(env_value NGROK_DOMAIN)"
if [[ "$TUNNEL" == 1 ]]; then
  if ! command -v ngrok >/dev/null; then
    warn "ngrok is not installed: running without a tunnel (see docs/whatsapp.md)"
  elif [[ -z "$NGROK_DOMAIN" ]]; then
    warn "NGROK_DOMAIN is not set in backend/.env: running without a tunnel (see docs/whatsapp.md)"
  else
    info "Starting ngrok on https://$NGROK_DOMAIN (log: backend/logs/ngrok.log)"
    ngrok http "$BACKEND_PORT" --url="https://$NGROK_DOMAIN" --log=stdout > "$LOG_DIR/ngrok.log" 2>&1 &
    PIDS+=("$!")
    PUBLIC_URL="https://$NGROK_DOMAIN"

    verify_token="$(env_value WHATSAPP_VERIFY_TOKEN)"
    tunnel_ok=0
    for _ in $(seq 1 20); do
      kill -0 "${PIDS[-1]}" 2>/dev/null || break
      if [[ "$(curl -s -m 5 "$PUBLIC_URL$WEBHOOK_PATH?hub.mode=subscribe&hub.verify_token=$verify_token&hub.challenge=ping")" == "ping" ]]; then
        tunnel_ok=1; break
      fi
      sleep 1
    done
    if [[ "$tunnel_ok" == 1 ]]; then
      info "Tunnel OK: Meta can reach the webhook"
    else
      warn "Could not verify the webhook through ngrok; see backend/logs/ngrok.log"
    fi
  fi
fi

echo
info "Ready. Press Ctrl+C to stop."
echo "    Local webhook : http://localhost:$BACKEND_PORT$WEBHOOK_PATH"
[[ -n "$PUBLIC_URL" ]] && echo "    Meta callback : $PUBLIC_URL$WEBHOOK_PATH"
echo "    Simulate      : python3 scripts/whatsapp_simulate.py \"Habari\" --url http://localhost:$BACKEND_PORT --org $ORG_ID"
echo "    Backend log   : tail -f backend/logs/backend.log"
echo

wait -n "${PIDS[@]}"
warn "A process exited; check the logs in backend/logs/"
