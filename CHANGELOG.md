## 0.2.3

- Added STM32H7S3 option-byte architecture and safety policy.
- Added guarded configuration for option-byte writes and internal-flash mass erase.
- Added documentation for current/programming option-byte registers and required device-specific sequencing.
- Kept option-byte mutation disabled by default pending hardware validation.
- Added explicit confirmation tokens for future mutation operations.

# Changelog

## 0.2.2

- Added J-Link RTT channel 0 support through the SEGGER RTT TELNET transport.
- Added persistent RTT-host management using J-Link GDB Server when no GDB session already owns the probe.
- Added `rtt_connect`, `rtt_read`, `rtt_write`, and `rtt_disconnect` MCP tools.
- Added explicit NRST pin controls: `nrst_assert`, `nrst_release`, and `nrst_pulse`.
- Added composite deployment workflow: erase -> program -> verify -> RTT connect -> NRST pulse.
- Added RTT configuration for TELNET port, bounded reads/writes, and optional control-block/search-range hints.
- Documented RTT ownership, reset behavior, and the recommended boot-log capture sequence.


## 0.2.1

- Reworked the project around a stateful `DebugSession`.
- Added J-Link and GDB ownership coordination.
- Added read-only safety mode and exact confirmation tokens.
- Added STM32H7S3 memory-region profile based on RM0477.
- Added Cortex-M fault decoder and structured snapshots.
- Added CMSIS-SVD peripheral/register metadata support.
- Added watchpoint, stop-reason, snapshot, and crash-diagnosis MCP tools.
- Added structured error codes and AI-oriented tool output.
- Added explicit external-NOR safety boundary; generic programming/erase are not falsely advertised as supported.
- Added unit tests and Linux/macOS CI configuration.
- Updated SEGGER command-line probe selection to documented `-USB` form.

## 0.2.1 - STM32H7S3I8T6 / XSPI1 board profile

- Added exact board profile for STM32H7S3I8T6 (LQFP176).
- Switched external-memory configuration from generic XSPI2 defaults to XSPI1 at 0x90000000.
- Added 512-Mbit / 64-MiB Macronix MX25UW51245GXDI00 configuration.
- Added expected RDID `C2 81 3A` and `HAL_XSPI_SIZE_512MB` metadata.
- Added board-specific bring-up documentation and regression tests.
- Kept external NOR programming disabled until a validated loader/programmer backend exists.
