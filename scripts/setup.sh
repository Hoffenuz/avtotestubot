#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> venv yaratilmoqda..."
python3 -m venv venv

echo "==> kutubxonalar o'rnatilmoqda..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> .env yaratildi — BOT_TOKEN ni to'ldiring!"
fi

echo ""
echo "Tayyor! Botni ishga tushirish:"
echo "  ./scripts/start.sh"
