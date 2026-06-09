#!/usr/bin/env bash
set -euo pipefail

mkdir -p tests
touch tests/__init__.py
touch tests/test_api.py

echo "Test scaffold created under ./tests"