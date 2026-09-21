#!/usr/bin/env bash
set -euo pipefail

for tool in JLinkExe JLinkGDBServer; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "OK: $tool -> $(command -v "$tool")"
  else
    echo "MISSING: $tool"
  fi
done

for tool in arm-none-eabi-gdb gdb-multiarch; do
  if command -v "$tool" >/dev/null 2>&1; then
    echo "OK: $tool -> $(command -v "$tool")"
  fi
done
