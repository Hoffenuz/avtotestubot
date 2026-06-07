#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d venv ]; then
  echo "venv topilmadi. Avval: ./scripts/setup.sh"
  exit 1
fi

exec ./venv/bin/python run.py
