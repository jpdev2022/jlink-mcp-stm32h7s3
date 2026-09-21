# Hardware Bring-Up

## 1. Verify J-Link

```text
JLinkExe
device STM32H7S3L8
si SWD
speed 4000
connect
halt
regs
```

## 2. Verify internal flash

```text
mem 0x08000000 100
```

## 3. Verify external flash

Determine the actual XSPI controller and mapping from the board design/firmware.

Potential mappings to investigate:

```text
XSPI1: 0x90000000
XSPI2: 0x70000000
```

Do not assume either.

## 4. If external flash fails

Check:

1. flash part number
2. JEDEC ID
3. XSPI instance
4. pin mux
5. clock/timing
6. memory-mapped mode
7. J-Link device support
8. external flash loader support

The MCP should not implement a custom flash algorithm until J-Link support has been evaluated.
