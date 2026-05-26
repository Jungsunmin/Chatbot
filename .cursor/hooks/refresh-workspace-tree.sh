#!/usr/bin/env bash
# 에이전트 루프(stop) 종료 시 디스크 기준 파일 트리 스냅샷 갱신 — 탐색기 동기화 보조
set -euo pipefail

ROOT="${CURSOR_PROJECT_DIR:-$(pwd)}"
cd "$ROOT" 2>/dev/null || exit 0

UTC_NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
BRANCH="$(git branch --show-current 2>/dev/null || echo unknown)"

write_tree() {
  local out="$1"
  {
    echo "# Workspace tree snapshot"
    echo "# updated_utc: ${UTC_NOW}"
    echo "# branch: ${BRANCH}"
    echo ""
    find . -not -path './.git/*' -not -path './.git' 2>/dev/null | LC_ALL=C sort
  } >"$out"
}

mkdir -p .cursor docs
write_tree ".cursor/workspace-tree.txt"
write_tree "docs/PROJECT_TREE.md"

exit 0
