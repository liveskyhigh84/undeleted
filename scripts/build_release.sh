#!/bin/bash
set -e
cd "$(dirname "$0")/.."
./.venv/bin/pyinstaller --onefile --name taskguardian-bin --paths . taskguardian.py
echo "Built: dist/taskguardian-bin"
./dist/taskguardian-bin --help > /dev/null && echo "Smoke test passed"
