#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8765}"
APP_URL="http://${HOST}:${PORT}/app/"

if [ ! -x .venv/bin/python ]; then
  echo "[setup] .venv not found; preparing local environment"
  python scripts/setup_venv.py
fi

.venv/bin/python - "$HOST" "$PORT" <<'PY'
import socket
import sys

host = sys.argv[1]
port = int(sys.argv[2])
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        if sock.connect_ex((host, port)) == 0:
            print(f"[start_failed] {host}:{port} is already in use.", file=sys.stderr)
            print("Stop the existing gateway or start with another PORT, for example: PORT=8766 bash scripts/dev_start_agent_app.sh", file=sys.stderr)
            raise SystemExit(1)
except PermissionError:
    print(f"[warn] Cannot probe {host}:{port} in this environment; uvicorn will report any bind error.", file=sys.stderr)
PY

echo "[1/2] Refreshing projections"
.venv/bin/python scripts/refresh_views.py --mode full

echo "[2/2] Starting Research Agent Cockpit gateway"
echo "[open] ${APP_URL}"
echo "[note] Do not open web/app with python -m http.server; it requires /api/* from this gateway."
exec .venv/bin/python -m uvicorn backend.agent_gateway.app:app --reload --host "$HOST" --port "$PORT"
