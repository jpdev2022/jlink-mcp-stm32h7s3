# STM32 J-Link MCP

AI-native hardware debugging and firmware-engineering interface for **STM32H7S3** using **SEGGER J-Link**.

This project is deliberately more than a thin wrapper around `JLinkExe`. It provides a stateful semantic layer for AI agents such as Claude Code, Codex, and Hermes while keeping SEGGER's J-Link tools as the low-level hardware backend.

## Design goals

- **Stateful debug session:** J-Link and GDB ownership are coordinated instead of being independent subprocesses.
- **Semantic tools:** expose target, memory, flash, GDB, Cortex-M fault, SVD, XSPI, and workflow operations.
- **AI-friendly output:** return compact structured evidence and stable error codes instead of terminal transcripts where possible.
- **STM32H7S3 specialization:** encode verified memory-map facts and Cortex-M diagnostics without pretending that a board-specific external NOR configuration is universal.
- **Safety:** read-only mode, bounded writes, explicit confirmation for destructive operations, and raw-command escape hatch disabled by default.
- **Extensibility:** J-Link, GDB, target profiles, SVD, and diagnostics are separate layers so additional STM32 families or probe backends can be added later.

## Current hardware profile

The checked-in example configuration is tailored to the current custom target:

- **MCU:** STM32H7S3I8T6, LQFP176
- **SEGGER J-Link device name:** `STM32H7S3I8`
- **External memory:** XSPI1
- **NOR:** assumed Macronix `MX25UW51245GXDI00`, 512 Mbit / 64 MiB
- **Memory-mapped base:** `0x90000000`
- **Expected RDID:** `C2 81 3A`

This is a board profile, not a claim that the external NOR is currently initialized. See `docs/BOARD_STM32H7S3I8T6_XSPI1.md` before enabling any programming workflow.

## Architecture

```text
AI Agent (Claude / Codex / Hermes)
              |
              | MCP / stdio
              v
      +---------------------+
      | Semantic MCP tools  |
      +----------+----------+
                 |
                 v
      +---------------------+
      | DebugSessionManager |
      | state / ownership   |
      | safety / locking    |
      +----+-----------+----+
           |           |
           v           v
    +-----------+   +-----------+
    | J-Link    |   | GDB       |
    | backend   |   | session   |
    +-----+-----+   +-----+-----+
          |               |
          v               v
     JLinkExe        JLinkGDBServer
          |               |
          +-------+-------+
                  |
                J-Link
                  |
                 SWD
                  |
             STM32H7S3
          /       |        \
       Flash     SRAM      XSPI
                            |
                       External NOR
```

### Important ownership rule

Do not concurrently use `JLinkExe` and GDB to control the same target. The session manager treats GDB as an owner of the live debug connection while a GDB session is active. Low-level one-shot J-Link operations should be used before/after the GDB session, or only when the session explicitly permits them.

## STM32H7S3 memory-map facts

The STM32H7Rx/7Sx reference manual places the following windows in the Cortex-M7 address space:

- User flash: `0x08000000` upward.
- System flash: `0x1FF00000` to `0x1FF1FFFF`.
- DTCM RAM: `0x20000000` to `0x2002FFFF`.
- AXI SRAM starts at `0x24000000`.
- SRAM1/SRAM2 are in the `0x30000000` region.
- XSPI1 window: `0x90000000` to `0x9FFFFFFF`.
- XSPI2 window: `0x70000000` to `0x7FFFFFFF`.

The **address window does not prove that an external memory is fitted, initialized, or memory-mapped on your board**. The board schematic and firmware configuration must determine the actual external NOR connection.

## External NOR policy

External NOR is intentionally not treated as a generic internal-flash equivalent.

There are three different operations:

1. **Read a memory-mapped NOR** — requires the MCU's XSPI controller and pins to already be configured.
2. **Program/erase NOR** — requires a valid J-Link flash loader or a target-side programming mechanism for the exact flash/controller/board.
3. **Probe/identify NOR** — may require executing controller-specific commands or firmware; a CPU memory read alone is not sufficient.

`external_flash_program` and `external_flash_erase` are disabled unless explicitly enabled in configuration. Do not enable them merely because the CPU window is `0x70000000` or `0x90000000`.

SEGGER documents an important distinction: `VerifyBin` performs a memory read/compare and does **not** initialize an external QSPI/XSPI interface; `LoadFile` can use a flash download/loader mechanism. Therefore this project does not claim that `verifybin` can independently access an uninitialized external NOR.

## Hardware-profile sources

The checked-in STM32H7S3I8T6/XSPI1 values are based on the ST STM32H7S3I8 product/datasheet and RM0477 memory map, SEGGER's supported-device database, ST's NUCLEO-H7S3L8 documentation identifying the 256-Mbit NOR family, and Macronix documentation for the 512-Mbit density equivalent. The exact custom-board BOM and schematic remain the authoritative source for the assembled hardware.

## Requirements

- Python 3.10+
- SEGGER J-Link Software and Documentation Pack
- J-Link probe
- ARM GDB (`arm-none-eabi-gdb` or `gdb-multiarch`)
- Optional firmware ELF with debug information
- Optional CMSIS-SVD file for peripheral/register semantics

SEGGER supports J-Link Commander and J-Link GDB Server on Linux and macOS.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e ".[dev]"
cp config.example.yaml config.yaml
```

Edit `config.yaml`, then:

```bash
stm32-jlink-mcp
```

Configuration path can be overridden with:

```bash
export STM32_JLINK_MCP_CONFIG=/absolute/path/config.yaml
```

## Direct hardware smoke test

Before involving MCP, validate J-Link itself:

```text
JLinkExe
Device STM32H7S3I8
SI SWD
Speed 4000
Connect
Halt
Regs
Mem8 0x08000000, 0x40
```

SEGGER recommends specifying the target device explicitly because device-specific handling may be required during connect/reset.

## MCP tool groups

### Probe / target

- `probe_list`
- `jlink_connect`
- `jlink_disconnect`
- `jlink_status`
- `target_identify`
- `target_status`
- `target_reset`
- `target_halt`
- `target_run`
- `target_step`

### Memory / registers

- `memory_read`
- `memory_write`
- `registers_read`
- `register_read`
- `register_write`

### Internal flash

- `flash_program`
- `flash_verify`
- `flash_erase`

### GDB / source debugging

- `debug_start`
- `debug_stop`
- `debug_continue`
- `debug_pause`
- `debug_step`
- `debug_breakpoint_set`
- `debug_breakpoint_clear`
- `debug_watchpoint_set`
- `debug_watchpoint_clear`
- `debug_stop_reason`
- `debug_backtrace`
- `read_variable`

### ELF / SVD

- `load_symbols`
- `resolve_address`
- `resolve_symbol`
- `svd_info`
- `peripheral_info`
- `register_info`
- `register_read`

### STM32 diagnostics

- `stm32_fault_info`
- `stm32_snapshot`
- `stm32_reset_reason`
- `boot_diagnose`

### XSPI / external memory

- `external_flash_info`
- `external_flash_read`
- `external_flash_test`
- `external_flash_program`
- `external_flash_erase`

### Workflows / expert escape hatches

- `flash_and_verify`
- `diagnose_crash`
- `jlink_command` (disabled by default)

## Safety model

Configuration supports:

```yaml
safety:
  mode: read_only
```

In read-only mode, target inspection and diagnostics remain available while writes/program/erase are denied.

Destructive or target-modifying operations can require exact confirmation tokens. The MCP server does not interpret a natural-language phrase such as "yes" as authorization.

## Testing

Fast tests do not require J-Link hardware:

```bash
pytest
ruff check .
```

Hardware tests are marked separately:

```bash
pytest -m hardware
```

They are intentionally not part of normal CI unless a self-hosted runner with the required hardware is configured.

## Project status

This is an engineering-focused v0.2 foundation. The core architecture is intended to be production-oriented, but board-specific external NOR programming still requires validation against the actual schematic, NOR part number, XSPI instance/configuration, and programming method.

Do not use this repository as a substitute for SEGGER documentation, the STM32 reference manual/datasheet, or your board's schematic.

## RTT and deployment sequence

J-Link RTT is supported as a first-class diagnostic transport. The preferred board workflow is:

```text
erase -> program -> verify -> RTT connect -> NRST pulse -> capture boot logs
```

Available MCP tools:

- `rtt_connect`
- `rtt_read`
- `rtt_write`
- `rtt_disconnect`
- `nrst_assert`
- `nrst_release`
- `nrst_pulse`
- `program_verify_rtt_nrst`

RTT uses SEGGER's local RTT TELNET transport and channel 0. When no GDB session is already active, the MCP starts a persistent J-Link GDB Server solely to maintain the J-Link connection required by RTT. If GDB is already active, RTT attaches to its configured RTT TELNET port.

See `docs/RTT_AND_PROGRAMMING_SEQUENCE.md` for ownership, reset, and RTT control-block guidance.

## Option bytes

STM32H7S3 option-byte inspection is exposed separately from ordinary memory/register access.

Planned/guarded operations:

- `option_bytes_read`
- `option_bytes_write`
- `option_bytes_mass_erase`

Option-byte writes and mass erase are disabled by default in configuration because
they are persistent device configuration changes. The implementation must use the
STM32H7S3-specific FLASH option-byte sequence; it must not guess a generic
`J-Link Commander` command or treat option bytes as ordinary RAM/register writes.

See `docs/OPTION_BYTES.md`.
