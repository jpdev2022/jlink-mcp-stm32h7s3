# STM32 J-Link MCP

AI-native MCP server for STM32H7S3 development through SEGGER J-Link.

Supports Linux and macOS and is designed for Claude Code, Codex, Hermes, and other MCP hosts.

## Architecture

```text
AI Agent
   |
   | MCP / stdio
   v
STM32 J-Link MCP
   |-- target control
   |-- memory/registers
   |-- flash
   |-- XSPI/OctoSPI diagnostics
   |-- GDB debugging
   |-- Cortex-M fault decoding
   |-- ELF/DWARF symbols
   |
   +--> J-Link Commander
   +--> J-Link GDB Server
             |
             v
          STM32H7S3
             |
             v
        External NOR flash
```

The MCP layer is intentionally a semantic layer over J-Link rather than a replacement for J-Link.

## Requirements

- Python 3.10+
- SEGGER J-Link Software and Documentation Pack
- J-Link probe
- ARM GDB (`arm-none-eabi-gdb` or `gdb-multiarch`)
- Optional firmware ELF with debug symbols

SEGGER provides J-Link Commander and J-Link GDB Server for Linux and macOS.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e ".[dev]"
cp config.example.yaml config.yaml
```

Edit `config.yaml`.

Then:

```bash
stm32-jlink-mcp
```

## First hardware validation

Before using MCP, verify the probe directly:

```text
JLinkExe
device STM32H7S3L8
si SWD
speed 4000
connect
halt
regs
mem 0x08000000 100
```

For external flash, use the address configured for the actual board. Common STM32 XSPI memory-mapped regions to investigate are `0x70000000` for XSPI2 and `0x90000000` for XSPI1, but do not assume either without checking the board.

## MCP tools

Connection:
- `jlink_connect`
- `jlink_disconnect`
- `jlink_status`

Target:
- `target_reset`
- `target_halt`
- `target_run`
- `target_step`
- `target_status`

Memory:
- `memory_read`
- `memory_write`
- `registers_read`

Flash:
- `flash_program`
- `flash_verify`
- `flash_erase`

External flash:
- `external_flash_info`
- `external_flash_read`
- `external_flash_test`

GDB:
- `debug_start`
- `debug_stop`
- `debug_continue`
- `debug_pause`
- `debug_step`
- `debug_breakpoint_set`
- `debug_breakpoint_clear`
- `debug_backtrace`

STM32 diagnostics:
- `stm32_fault_info`
- `boot_diagnose`

Symbols:
- `load_symbols`
- `resolve_address`
- `resolve_symbol`
- `read_variable`

Escape hatch:
- `jlink_command`

Prefer semantic MCP tools over the raw command tool.

## Safety

Flash erase is destructive and requires explicit confirmation by default.

Do not commit passwords, tokens, private keys, or machine-specific secrets.

## MCP host example

```json
{
  "mcpServers": {
    "stm32-jlink": {
      "command": "/absolute/path/to/repo/.venv/bin/stm32-jlink-mcp"
    }
  }
}
```

## Development

```bash
pytest
ruff check .
```

The server uses the official MCP Python SDK and stdio transport for local MCP hosts.
