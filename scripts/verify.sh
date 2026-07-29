#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
export PYTHONDONTWRITEBYTECODE=1

cd "$PROJECT_DIR"
"$PYTHON_BIN" scripts/verify.py
"$PYTHON_BIN" scripts/smoke_server.py

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git diff --check
fi
