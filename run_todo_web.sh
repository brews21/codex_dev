#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

venv_path="$(pwd)/.venv"

if [ "${VIRTUAL_ENV:-}" != "$venv_path" ]; then
  # shellcheck source=/dev/null
  source ".venv/bin/activate"
fi

python -m pip install -r requirements.txt

export PYTHONPATH="src"
exec flask --app codex_dev.web:create_app run --host 127.0.0.1 --port 5000
