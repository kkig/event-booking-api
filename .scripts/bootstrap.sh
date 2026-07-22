#!/usr/bin/env bash
# Post-create script for the backend-app devcontainer
# Cancel on errors, unset variables, and failed pipes
set -euo pipefail

echo "Bootstrapping backend development environment..."

# Determine repository root from this script's location
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"

echo "Repository root: $REPO_ROOT"
echo "Backend: $BACKEND_DIR"

if [[ ! -f "$BACKEND_DIR/pyproject.toml" ]]; then
    echo "Error: pyproject.toml not found in $BACKEND_DIR"
    exit 1
fi

if [[ ! -f "$BACKEND_DIR/uv.lock" ]]; then
    echo "Error: uv.lock not found in $BACKEND_DIR"
    exit 1
fi

if ! command -v uv >/dev/null; then
    echo "Error: 'uv' is not installed. Please install 'uv' before running this script."
    exit 1
fi

if ! command -v git >/dev/null; then
    echo "Error: 'git' is not installed. Please install 'git' before running this script."
    exit 1
fi

echo "Installing Python dependencies..."
cd "$BACKEND_DIR"
uv sync --frozen

if ! command -v pre-commit >/dev/null; then
    echo "Installing pre-commit..."
    uv tool install pre-commit --with pre-commit-uv
fi

# Install pre-commit hooks only if inside a Git repository
cd "$REPO_ROOT"

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Installing Git hooks..."
    pre-commit install --install-hooks
else
    echo "Not a Git repository. Skipping pre-commit hook installation."
fi

echo "Done."
