#!/usr/bin/env bash
# Start AEGIS frontend, API, and Streamlit RAG dashboard together.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck source=/dev/null
  source .env
  set +a
fi

port_busy() {
  lsof -i ":$1" -t >/dev/null 2>&1
}

ensure_backend_venv() {
  if [[ ! -d backend/.venv ]]; then
    echo "Creating backend venv..."
    python3 -m venv backend/.venv
  fi
  backend/.venv/bin/pip install -q -r backend/requirements.txt
}

PIDS=()

cleanup() {
  echo ""
  echo "Stopping dev processes..."
  for pid in "${PIDS[@]}"; do
    kill "$pid" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

echo "=== AEGIS dev stack ==="

ensure_backend_venv

if port_busy 8000; then
  echo "API already on http://127.0.0.1:8000"
else
  echo "Starting API (uvicorn :8000)..."
  (cd backend && source .venv/bin/activate && uvicorn main:app --host 127.0.0.1 --port 8000) &
  PIDS+=($!)
  sleep 1
fi

if port_busy 8501; then
  echo "Streamlit already on http://127.0.0.1:8501"
else
  echo "Starting RAG dashboard (streamlit :8501)..."
  (cd backend && source .venv/bin/activate && streamlit run streamlit_rag_dashboard.py --server.headless true) &
  PIDS+=($!)
  sleep 1
fi

VITE_PORT=8080
if port_busy 8080; then
  VITE_PORT=8081
fi
if port_busy "$VITE_PORT" && [[ "$VITE_PORT" == 8081 ]]; then
  echo "Frontend already running (check http://localhost:8080 or :8081)"
else
  echo "Starting frontend (vite)..."
  npm run dev -- --port "$VITE_PORT" --strictPort false &
  PIDS+=($!)
fi

echo ""
echo "  App (React)     → http://localhost:${VITE_PORT:-8080}/"
echo "  API             → http://127.0.0.1:8000/docs"
echo "  RAG dashboard   → http://127.0.0.1:8501"
echo ""
echo "Press Ctrl+C to stop processes started by this script."

wait
