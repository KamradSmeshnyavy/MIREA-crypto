#!/usr/bin/env bash
set -euo pipefail

PYTHON="/Users/kamradsmeshnyavy/Downloads/labs-documents/Методы и средства криптографической защиты информации/practice/.venv/bin/python"

"$PYTHON" -m pip install --upgrade pyinstaller
"$PYTHON" -m PyInstaller --noconfirm --windowed --onefile \
  --name "crypto-practice" \
  main.py

echo "Build complete. See ./dist/crypto-practice or ./dist/crypto-practice.app"
