#!/bin/bash
# Package management
uv sync --project backend

# Security & Quality tooling
uv tool install pre-commit --with pre-commit-uv
pre-commit install --install-hooks
