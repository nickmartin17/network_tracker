#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$ROOT_DIR/.venv/bin/python"
API_PORT="${API_PORT:-8000}"
UI_PORT="${UI_PORT:-8501}"
API_URL="http://127.0.0.1:${API_PORT}"

if [ ! -x "$PYTHON" ]; then
  echo "Could not find $PYTHON"
  echo "Create the virtual environment and install dependencies first:"
  echo "  python3 -m venv .venv"
  echo "  .venv/bin/pip install -r requirements.txt"
  exit 1
fi

cd "$ROOT_DIR"

cleanup() {
  if [ -n "${API_PID:-}" ] && kill -0 "$API_PID" 2>/dev/null; then
    kill "$API_PID"
  fi
}
trap cleanup EXIT INT TERM

echo "Starting API on ${API_URL}"
"$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port "$API_PORT" &
API_PID="$!"

echo "Waiting for API..."
for _ in $(seq 1 30); do
  if "$PYTHON" -c "import urllib.request; urllib.request.urlopen('${API_URL}/health', timeout=1)" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

echo "Starting Network Tracker UI on http://127.0.0.1:${UI_PORT}"
NETWORK_TRACKER_API_URL="$API_URL" "$PYTHON" -m streamlit run streamlit_app.py \
  --server.address 127.0.0.1 \
  --server.port "$UI_PORT"
