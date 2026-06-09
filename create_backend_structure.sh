#!/usr/bin/env bash
set -euo pipefail

mkdir -p backend/app/api
mkdir -p backend/app/core
mkdir -p backend/app/schemas
mkdir -p backend/app/services
mkdir -p backend/models

touch backend/app/main.py
touch backend/app/api/endpoints.py
touch backend/app/core/config.py
touch backend/app/core/ml_engine.py
touch backend/app/schemas/payload.py
touch backend/app/services/grading_service.py
touch backend/requirements.txt

echo "Backend scaffold created under ./backend"
