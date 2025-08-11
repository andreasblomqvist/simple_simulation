#!/usr/bin/env bash

# SimpleSim Full Restart Script
# - Stops any running servers
# - Ensures backend venv and dependencies
# - Starts FastAPI backend (port 8000) and waits for health
# - Ensures frontend deps
# - Starts Vite dev server (port 3000) and waits for readiness

set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_PORT="8000"
FRONTEND_PORT="3000"
BACKEND_LOG="$PROJECT_ROOT/backend/logs/dev-backend.log"
FRONTEND_LOG="$PROJECT_ROOT/frontend/dev-frontend.log"

info() { echo -e "[INFO] $*"; }
warn() { echo -e "[WARN] $*"; }
error() { echo -e "[ERROR] $*"; }

wait_for_http() {
  local url="$1"; local name="$2"; local attempts="${3:-60}"; local delay="${4:-1}"
  for ((i=1; i<=attempts; i++)); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      info "$name is ready at $url"
      return 0
    fi
    sleep "$delay"
  done
  return 1
}

wait_for_port() {
  local port="$1"; local name="$2"; local attempts="${3:-60}"; local delay="${4:-1}"
  for ((i=1; i<=attempts; i++)); do
    if (echo > "/dev/tcp/127.0.0.1/$port") >/dev/null 2>&1; then
      info "$name port $port is accepting connections"
      return 0
    fi
    sleep "$delay"
  done
  return 1
}

cd "$PROJECT_ROOT"

# 1) Stop any existing servers
if [[ -x "$PROJECT_ROOT/scripts/kill-servers.sh" ]]; then
  info "Stopping existing servers via scripts/kill-servers.sh"
  "$PROJECT_ROOT/scripts/kill-servers.sh" || true
else
  warn "scripts/kill-servers.sh not found or not executable; attempting lightweight stop"
  pkill -f uvicorn 2>/dev/null || true
  pkill -f vite 2>/dev/null || true
  pkill -f "npm.*dev" 2>/dev/null || true
fi

# 2) Backend: ensure venv and deps
info "Ensuring Python virtual environment (.venv) exists"
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

if [[ -f "$PROJECT_ROOT/backend/requirements.txt" ]]; then
  info "Installing backend dependencies (pip)"
  pip install -r "$PROJECT_ROOT/backend/requirements.txt"
else
  warn "backend/requirements.txt not found; skipping pip install"
fi

# 3) Backend: start FastAPI
info "Starting FastAPI backend on port $BACKEND_PORT"
mkdir -p "$PROJECT_ROOT/backend/logs"
# Note: run from project root so module path backend.main:app resolves
nohup uvicorn backend.main:app --reload --port "$BACKEND_PORT" >"$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
info "Backend PID: $BACKEND_PID (logs: $BACKEND_LOG)"

# 4) Wait for backend health
if wait_for_http "http://127.0.0.1:$BACKEND_PORT/health" "Backend health" 90 1; then
  info "Backend is healthy"
else
  error "Backend did not become healthy. Check logs: $BACKEND_LOG"
  exit 1
fi

# 5) Frontend: ensure deps
info "Ensuring frontend dependencies (npm install)"
pushd "$PROJECT_ROOT/frontend" >/dev/null
if [[ ! -d node_modules ]]; then
  npm install
else
  # Optional: quick check for missing lockfile/node_modules mismatch
  if [[ ! -f package-lock.json ]]; then
    warn "package-lock.json missing; running npm install"
    npm install
  fi
fi
popd >/dev/null

# 6) Frontend: start Vite dev server
info "Starting Vite dev server on port $FRONTEND_PORT"
nohup bash -lc "cd '$PROJECT_ROOT/frontend' && npm run dev -- --port $FRONTEND_PORT" >"$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
info "Frontend PID: $FRONTEND_PID (logs: $FRONTEND_LOG)"

# 7) Wait for frontend readiness (port and HTTP)
if wait_for_port "$FRONTEND_PORT" "Frontend (Vite)" 60 1; then
  # Give Vite a moment to compile initial build
  sleep 2
  wait_for_http "http://127.0.0.1:$FRONTEND_PORT" "Frontend HTTP" 60 1 || true
else
  warn "Frontend port $FRONTEND_PORT not responding yet; check logs: $FRONTEND_LOG"
fi

info "All set!"
echo
echo "Backend:  http://localhost:$BACKEND_PORT (health: /health)"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo
echo "Tail logs:"
echo "  tail -f '$BACKEND_LOG'"
echo "  tail -f '$FRONTEND_LOG'"
echo
