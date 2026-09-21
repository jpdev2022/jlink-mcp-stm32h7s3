# RTT and preferred programming/reset sequence

The preferred deployment workflow for this board is:

```text
ERASE
  -> PROGRAM
  -> VERIFY
  -> RTT CONNECT
  -> NRST ASSERT
  -> NRST RELEASE
  -> capture application boot logs
```

## Why RTT is connected before NRST release

RTT requires an active J-Link debug connection. The MCP starts a persistent J-Link GDB Server transport when no GDB session already owns the probe, then attaches to its RTT TELNET channel. SEGGER documents that the RTT client itself does not establish the debug connection; another J-Link tool must maintain it.

The MCP uses RTT channel 0, matching the channel supported by the simple J-Link RTT Client terminal path. The implementation uses the J-Link RTT TELNET protocol directly so the MCP can expose bounded read/write operations instead of an interactive terminal process.

## NRST behavior

`nrst_assert` sends J-Link Commander `r0` and `nrst_release` sends `r1`. SEGGER documents these as clear/set RESET-pin operations. This is a physical reset-pin operation, not merely a CPU reset request.

`nrst_pulse` performs:

1. `r0`
2. delay `assert_ms`
3. `r1`
4. delay `release_wait_ms`

The default values are 50 ms asserted and 100 ms after release. Tune these to the board's reset circuit and boot timing.

## Important ownership rule

Do not run a separate J-Link Commander, J-Link GDB Server, RTT Viewer, or RTT Client against the same probe/session while MCP owns it. RTT itself can coexist with a debugger, but multiple host applications consuming the same RTT stream can steal/fragment data.

## RTT control block

By default the MCP lets J-Link auto-detect the RTT control block. If the application places the RTT control block outside the RAM ranges known to the J-Link DLL, configure a fixed address or search range. For Cortex-M targets, keep the RTT control block and buffers in accessible internal RAM; do not place them in the external XSPI NOR unless there is a deliberate initialization strategy.

The configuration supports:

```yaml
rtt:
  control_block: 0x24000000
  search_ranges:
    - "0x24000000 0x00072000"
```

These are examples only. Use the actual linker placement from the firmware.

## Preferred MCP call sequence

For manual control:

```text
flash_erase(confirmation="ERASE_INTERNAL_FLASH")
flash_program(..., confirmation="PROGRAM_INTERNAL_FLASH")
flash_verify(...)
rtt_connect()
nrst_pulse()
rtt_read()
```

For an automated deployment:

```text
program_verify_rtt_nrst(
    image=..., 
    address=..., 
    erase_confirmation="ERASE_INTERNAL_FLASH",
    program_confirmation="PROGRAM_INTERNAL_FLASH"
)
```

The composite operation intentionally returns each stage separately so an AI agent can identify whether failure occurred during erase, program, verify, RTT attach, or reset.
