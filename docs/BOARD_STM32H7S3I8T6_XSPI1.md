# STM32H7S3I8T6 + XSPI1 512-Mbit NOR board profile

This profile is for the custom board described in the project issue/design notes:

- MCU: **STM32H7S3I8T6**, LQFP176
- Debug: SWD/J-Link
- External memory controller: **XSPI1**
- External NOR: **512 Mbit / 64 MiB**
- Assumed NOR: **Macronix MX25UW51245GXDI00**
- CPU memory-mapped XSPI1 window: **0x90000000**
- NOR capacity: **0x04000000 bytes**
- Expected RDID: **C2 81 3A**
- Expected STM32 HAL memory-size setting: `HAL_XSPI_SIZE_512MB`

## Why these values are used

ST's STM32H7S3I8 product page lists the LQFP176 ordering code `STM32H7S3I8T6`, while SEGGER's supported-device database names the J-Link target `STM32H7S3I8`. The MCP therefore keeps both values: the exact BOM part number for documentation and the SEGGER device identifier for J-Link commands.

The NUCLEO-H7S3L8 uses a 256-Mbit, 1.8-V Octo-SPI NOR. ST documentation and the board community identify the fitted part as `MX25UW25645GXDI00`. The current custom-board configuration assumes the same family at the next density, `MX25UW51245GXDI00`.

The 512-Mbit part is 64 MiB (`512,000,000` bits nominally; device organization is 64M x 8). Macronix documents 1.65-2.0 V operation and up to 200 MHz OctaBus operation for this family. The device RDID is `C2 81 3A`.

## XSPI1 address

For this STM32H7S3 family, the XSPI1 memory-mapped window begins at `0x90000000`. A 64-MiB device therefore occupies:

```text
0x90000000 .. 0x93FFFFFF
```

Do not confuse the CPU mapping with proof that the NOR is initialized. Reading `0x90000000` while XSPI1 is not configured can fail or produce a fault.

## XSPI initialization

The MCP intentionally does **not** invent the board's clock divider, dummy-cycle configuration, DTR configuration, delay settings, XSPIM I/O port, or chip-select timing. Those values depend on the actual board routing and the exact flash configuration.

ST's external-loader guidance for the NUCLEO-H7S3L8 demonstrates XSPI1 in Octo-SPI mode using NCS1. That is the starting point for this board profile, but the custom board must be checked against its schematic and firmware.

For the 512-Mbit device, the STM32 HAL nomenclature is slightly confusing: `HAL_XSPI_SIZE_512MB` represents **512 Mbit**, which corresponds to **64 MiB** of addressable NOR. The project records both the explicit byte capacity and the HAL setting to avoid ambiguity.

## Programming policy

Generic external-NOR programming remains disabled in the MCP until one of these is explicitly implemented and validated:

1. a SEGGER-compatible external flash loader for this exact XSPI1/flash combination;
2. a target-resident programmer/loader built from the board firmware; or
3. a dedicated XSPI indirect-mode programmer backend.

A memory-mapped read is not sufficient evidence that `loadfile` or generic J-Link flash programming can safely program the external NOR.

## Recommended first hardware validation

1. Connect J-Link and identify `STM32H7S3I8`.
2. Read target voltage and core status.
3. Halt the MCU.
4. Confirm the firmware has initialized XSPI1.
5. Read a small range from `0x90000000`.
6. Independently issue an XSPI RDID/SFDP transaction through the firmware/loader path.
7. Compare the live RDID against `C2 81 3A`.
8. Only after that validate external-memory programming.

Do not use the configured JEDEC ID as proof of live hardware identity; it is an expected value until a transaction has actually read it.

## Internal-memory profile note

The STM32H7S3 memory map has architectural windows larger than the minimum non-remapped TCM/AXI allocations because parts of the TCM and AXI SRAM are shared/remappable. RM0477 Rev. 8 defines the windows used by this MCP for safety classification:

```text
ITCM       0x00000000 .. 0x0002FFFF
User flash 0x08000000 .. 0x0800FFFF
System     0x1FF00000 .. 0x1FF1FFFF
DTCM       0x20000000 .. 0x2002FFFF
AXI SRAM   0x24000000 .. 0x24071FFF
SRAM1/2    0x30000000 .. 0x30007FFF
BKPSRAM    0x38800000 .. 0x38800FFF
XSPI2      0x70000000 .. 0x7FFFFFFF
XSPI1      0x90000000 .. 0x9FFFFFFF
```

These are address-map classifications, not a claim that every byte is simultaneously usable in every remap/ECC/security state. The MCP should eventually read the relevant option/configuration state before giving an AI agent a stronger statement about effective RAM availability.
