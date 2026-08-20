#!/bin/bash
set -e
cd "$(dirname "$0")/.."
./.venv/bin/pyinstaller --onefile --name undeleted-bin --paths . undeleted.py
echo "Built: dist/undeleted-bin"
./dist/undeleted-bin --help > /dev/null && echo "Smoke test passed"
