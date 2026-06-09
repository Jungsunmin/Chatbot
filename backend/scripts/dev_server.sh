#!/usr/bin/env bash
# 실기기(Expo Go)에서 접속하려면 0.0.0.0 바인딩 필수 — 127.0.0.1 만 쓰면 API offline
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate
exec uvicorn app.main:app --host 0.0.0.0 --port 8001 "$@"
