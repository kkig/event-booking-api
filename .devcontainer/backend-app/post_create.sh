#!/usr/bin/env bash
# Post-create script for the backend-app devcontainer
# Cancel on errors, unset variables, and failed pipes
set -euo pipefail

echo "Installing Python dependencies..."
cd /workspace/backend
uv sync

echo "Installing pre-commit hooks..."
if ! command -v pre-commit >/dev/null; then
    uv tool install pre-commit --with pre-commit-uv
fi
pre-commit install --install-hooks

echo "Done."
