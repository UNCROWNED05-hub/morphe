#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
cd "$DIR"

if [ ! -f ".venv/bin/python" ] && [ ! -f ".venv/Scripts/python.exe" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
fi

PYTHON=".venv/bin/python"
if [ ! -f "$PYTHON" ]; then
    PYTHON=".venv/Scripts/python.exe"
fi

echo "Starting MORPHE Dashboard at http://localhost:8501"
$PYTHON -m streamlit run app.py
