#!/usr/bin/env bash
# Voice Agent Backend — Start Script (Linux/macOS)
# Usage: bash start_server.sh

set -e
cd "$(dirname "$0")"

if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Please copy ../.env.example to .env and configure it."
    exit 1
fi

echo "Starting Voice Agent on http://localhost:8000 ..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
