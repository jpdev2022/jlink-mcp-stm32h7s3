#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e ".[dev]"
cp -n config.example.yaml config.yaml || true
printf '\nInstalled. Run: stm32-jlink-mcp\n'
