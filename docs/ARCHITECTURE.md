# Architecture

## Principles

1. **MCP is the semantic boundary.** The agent should ask for `diagnose_crash`, `external_flash_test`, or `register_info`, not reconstruct a J-Link command script from prose.
2. **J-Link remains the hardware engine.** The project intentionally does not reimplement the SWD/JTAG protocol.
3. **GDB owns source-level debugging.** GDB/MI is used for breakpoints, stepping, stack frames, expression evaluation, and runtime symbol-aware operations.
4. **A session owns the target.** Direct J-Link operations and GDB operations are serialized to prevent concurrent control of one probe/target.
5. **Board-specific behavior is explicit.** External NOR programming is not inferred from an address range.
6. **Tools return evidence, not terminal noise.** Stable error codes and structured fields are preferred.

## Layers

```text
mcp/server.py
    |
service.py
    |
+-- session.py ----------------- target ownership/state
+-- safety/policy.py ------------ authorization and limits
+-- probe/jlink.py -------------- J-Link Commander adapter
+-- gdb/session.py -------------- GDB + J-Link GDB Server adapter
+-- symbols.py ------------------ static ELF symbol index
+-- svd/parser.py --------------- CMSIS-SVD metadata
+-- diagnostics/cortex_m.py ----- Cortex-M fault decoding
+-- targets/stm32h7s3.py -------- verified STM32H7S3 memory windows
```

## Why one-shot J-Link Commander?

J-Link Commander is excellent for deterministic, scriptable low-level operations such as reset, halt, memory access, and flash programming. SEGGER documents command files and batch operation explicitly. A one-shot process is simple to recover after an error and avoids keeping a second persistent J-Link control connection alive.

The tradeoff is that process startup is more expensive and transcript parsing must be robust. If future performance requirements justify it, the `JLinkBackend` interface can be replaced with a J-Link SDK/API implementation without changing the MCP/service layer.

## GDB ownership

When `debug_start` succeeds:

```text
DebugSession.gdb_active = true
```

Direct J-Link operations are rejected with `TARGET_OWNED_BY_GDB`. This prevents the common failure mode where one process has an active GDB remote connection and another process attempts to manipulate the same probe.

`debug_stop` releases ownership.

## Target state

The state machine is deliberately conservative:

```text
DISCONNECTED -> CONNECTED -> HALTED
                       \-> RUNNING
```

A state is an MCP-side observation, not a claim that the target can never have changed externally. `target_status` should be used when exact current hardware evidence matters.

## Error contract

Every tool returns either:

```json
{
  "success": true,
  "operation": "...",
  "data": {}
}
```

or:

```json
{
  "success": false,
  "operation": "...",
  "error": {
    "code": "TARGET_OWNED_BY_GDB",
    "message": "...",
    "recoverable": true
  }
}
```

Agents can use `code` for recovery logic without scraping prose.

## External flash

The STM32H7S3 address map has XSPI2 at `0x70000000-0x7FFFFFFF` and XSPI1 at `0x90000000-0x9FFFFFFF`. Those are CPU address windows. They are not evidence that an external NOR is physically connected or initialized.

The service therefore implements only safe memory-mapped read/test operations generically. Programming/erase operations are explicit unimplemented boundaries until a board-specific programmer backend is added.

A future backend should implement an interface similar to:

```python
class ExternalFlashProgrammer(Protocol):
    def probe(self) -> FlashIdentity: ...
    def read(self, offset: int, length: int) -> bytes: ...
    def program(self, image: Path, address: int) -> ProgramResult: ...
    def erase(self, start: int, end: int) -> EraseResult: ...
```

Possible implementations include a validated SEGGER flash loader, a target-resident programming routine, or a board-specific loader script. The choice depends on the exact NOR part and board design.

## SVD

The SVD parser intentionally handles the common CMSIS-SVD peripheral/register/field model. It does not attempt to become a complete SVD compiler: clusters, arrays, derived peripherals, and vendor-specific extensions should be added only when required by the actual STM32H7S3 SVD.

## ELF/DWARF

`ElfSymbols` indexes static symbol addresses. Runtime variable evaluation is delegated to GDB. This avoids implementing a complete DWARF location-expression interpreter in Python.
