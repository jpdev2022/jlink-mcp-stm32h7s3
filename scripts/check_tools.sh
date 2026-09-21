#!/usr/bin/env bash
set -u

echo "J-Link:"
command -v JLinkExe || echo "MISSING: JLinkExe"

echo "J-Link GDB Server:"
command -v JLinkGDBServer || echo "MISSING: JLinkGDBServer"

echo "GDB:"
command -v arm-none-eabi-gdb || command -v gdb-multiarch || echo "MISSING: ARM GDB"

echo "Python:"
python3 --version
