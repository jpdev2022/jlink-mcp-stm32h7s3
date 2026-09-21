# STM32H7S3 Hardware Bring-Up Checklist

This document is deliberately evidence-driven. Do not assume an external memory configuration from a linker address alone.

## 1. Probe and power

- Target is powered.
- J-Link is connected with correct SWD wiring.
- Target voltage is within the board's intended range.
- No other debugger is actively controlling the target.
- Confirm the J-Link serial if more than one probe is attached.

## 2. Direct J-Link smoke test

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

Record the complete transcript on the first successful connection.

## 3. Verify reset behavior

Use:

```text
Reset
Halt
Regs
```

Confirm that the PC and stack pointer are plausible for the current firmware image. Do not hard-code an expected PC unless the firmware image is known.

SEGGER supports reset variants and reset-after-bootloader strategies; use those deliberately when a bootloader or early hardware initialization makes ordinary reset/halt timing insufficient.

## 4. Internal flash

Before programming:

- Confirm target identity.
- Confirm the intended image path.
- Confirm the destination address for `.bin` images.
- Use `flash_program` with `PROGRAM_INTERNAL_FLASH` confirmation.
- Use `flash_verify` for `.bin` images.

J-Link `LoadFile` supports multiple image formats and can invoke flash programming support. Do not assume a `.bin` without an explicit destination address has the intended location.

## 5. Cortex-M fault capture

If the target halts unexpectedly, capture:

```text
registers
PC / LR / SP / xPSR
CFSR
HFSR
MMFAR
BFAR
SHCSR
ICSR
```

Then correlate PC to the ELF with `resolve_address` or GDB.

## 6. External XSPI/NOR

First establish from the schematic:

- XSPI instance: XSPI1 or XSPI2.
- CPU memory-mapped address.
- NOR manufacturer and exact part number.
- Bus width and protocol.
- DTR/STR mode.
- Dummy cycles.
- Maximum clock.
- Chip-select and reset pins.
- Firmware initialization sequence.

Only after firmware initializes XSPI should `external_flash_read` be expected to work.

SEGGER documents that `VerifyBin` is a memory read/compare and does not initialize an external QSPI interface. `LoadFile` may use a flash loader while programming, but the controller/pin state is not necessarily left initialized after the operation.

## 7. External flash validation sequence

```text
1. target_halt
2. inspect firmware state / PC
3. confirm XSPI clocks and GPIO through SVD
4. confirm XSPI controller configuration
5. external_flash_test
6. compare returned bytes with expected NOR contents
```

A passing memory read demonstrates CPU-side access to the mapped window. It does not prove the JEDEC identity unless a real identification transaction has been performed.

## 8. Current custom-board defaults

For the current board, `config.example.yaml` is already populated for:

- STM32H7S3I8T6 (LQFP176), J-Link device name `STM32H7S3I8`
- XSPI1 / NCS1
- Macronix MX25UW51245GXDI00, 512 Mbit / 64 MiB
- memory-mapped base `0x90000000`
- expected RDID `C2 81 3A`

These are expected configuration values, not live hardware observations. The board-specific document contains the validation sequence and the reasons generic external-flash programming remains disabled.
