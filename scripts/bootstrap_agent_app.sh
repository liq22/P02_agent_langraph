#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] Preparing .venv"
python scripts/setup_venv.py

echo "[2/4] Checking config"
if [ ! -f config/agent_gateway.yaml ]; then
  cp config/agent_gateway.yaml.example config/agent_gateway.yaml
  echo "Created config/agent_gateway.yaml from example. Edit it before starting the gateway."
fi

echo "[3/4] Refreshing projections"
.venv/bin/python scripts/refresh_views.py --mode full

echo "[4/4] Done"
echo "Next:"
echo "  1. edit config/agent_gateway.yaml"
echo "  2. .venv/bin/python -m uvicorn backend.agent_gateway.app:app --reload --port 8765"
echo "  3. open http://127.0.0.1:8765/app/"
