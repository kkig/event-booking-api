#!/bin/bash
# Package management
cd /workspace/backend
uv sync

# Security & Quality tooling
uv tool install pre-commit --with pre-commit-uv
pre-commit install --install-hooks
