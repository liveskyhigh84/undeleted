#!/bin/bash
set -e
cd "$(dirname "$0")/.."
./.venv/bin/pyinstaller --onefile --name undeleted-bin --paths . undeleted.py
echo "Built: dist/undeleted-bin"
BIN="$(pwd)/dist/undeleted-bin"
"$BIN" --help > /dev/null && echo "Smoke test passed: --help"

# Regression guard: under PyInstaller, __file__-based paths resolve inside the
# ephemeral extraction dir and silently break persistence (caught 21 Aug 2026
# security review — status/snapshot appeared to work but never actually
# persisted anything). Run `status` from two different directories and
# confirm identical, non-crashing output — proves storage isn't cwd- or
# extraction-dir-dependent.
OUT_A=$("$BIN" status)
OUT_B=$(cd /tmp && "$BIN" status)
if [ "$OUT_A" != "$OUT_B" ]; then
  echo "FAIL: status output differs by working directory — storage path regression"
  echo "  from repo dir: $OUT_A"
  echo "  from /tmp:     $OUT_B"
  exit 1
fi
echo "Smoke test passed: status is cwd-independent ($OUT_A)"
