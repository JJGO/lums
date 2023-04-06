#!/usr/bin/env bash
set -euo pipefail
if [[ ! -d env ]]; then
    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt
fi

source env/bin/activate

export PORT=
export DOMAIN=
export SERVERS=
uvicorn server:app --port "$PORT" --host 0.0.0.0
