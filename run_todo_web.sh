#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install -r requirements.txt

export PYTHONPATH="src"
exec .venv/bin/flask --app codex_dev.web:create_app run --host 127.0.0.1 --port 5000
