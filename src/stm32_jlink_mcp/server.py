from __future__ import annotations

import subprocess
import time
from typing import Any

from mcp.server import MCPServer
from pygdbmi.gdbcontroller import GdbController

from .core import Config, ElfSymbols, JLink, MCPError, load_config

cfg: Config = load_config()
jlink = JLink(cfg)
symbols = ElfSymbols()
gdb_server: subprocess.Popen[str] | None = None
gdb: GdbController | None = None

mcp = MCPServer(
    "stm32-jlink-mcp",
    instructions=(
        "Semantic STM32 debugging and programming through SEGGER J-Link. "
        "Prefer the specialized tools over jlink_command. "
        "Flash erase is destructive."
    ),
)


def ok(operation: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"success": True, "operation": operation, "data": data}


def fail(operation: str, exc: Exception) -> dict[str, Any]:
    if isinstance(exc, MCPError):
        return {"success": False, "operation": operation,
                "error_code": exc.code, "message": str(exc)}
    return {"success": False, "operation": operation,
            "error_code": "UNEXPECTED_ERROR", "message": str(exc)}


def call(operation: str, fn):
    try:
        return ok(operation, fn())
    except Exception as exc:
        return fail(operation, exc)


@mcp.tool()
def jlink_connect():
    """Connect to the configured STM32 target."""
    return call("jlink_connect", jlink.connect)


@mcp.tool()
def jlink_disconnect():
    """End the logical MCP-side session."""
    return ok("jlink_disconnect", {"disconnected": True})


@mcp.tool()
def jlink_status():
    """Return target and J-Link status."""
    return call("jlink_status", jlink.status)


@mcp.tool()
def target_reset():
    """Reset and resume the target."""
    return call("target_reset", jlink.reset)


@mcp.tool()
def target_halt():
    """Halt the target."""
    return call("target_halt", jlink.halt)


@mcp.tool()
def target_run():
    """Resume the target."""
    return call("target_run", jlink.run)


@mcp.tool()
def target_step():
    """Single-step using J-Link Commander."""
    return call("target_step", jlink.step)


@mcp.tool()
def target_status():
    """Return target state and registers."""
    return call("target_status", jlink.status)


@mcp.tool()
def memory_read(address: int, length: int):
    """Read target memory as bytes."""
    return call("memory_read", lambda: jlink.read_memory(address, length))


@mcp.tool()
def memory_write(address: int, data_hex: str):
    """Write target memory from a hexadecimal byte string."""
    def op():
        data = bytes.fromhex(data_hex)
        if len(data) > cfg.safety.max_memory_write_bytes:
            raise MCPError("Memory write exceeds configured safety limit",
                           "SAFETY_LIMIT")
        return jlink.write_memory(address, data)
    return call("memory_write", op)


@mcp.tool()
def registers_read():
    """Read Cortex-M registers."""
    return call("registers_read", jlink.registers)


@mcp.tool()
def flash_program(image: str, region: str = "internal_flash",
                  address: int | None = None):
    """Program an image through J-Link. External flash defaults to its configured mapping."""
    def op():
        if region == "external_flash" and address is None:
            address = cfg.external_flash.mapped_address
        return jlink.program(image, address)
    return call("flash_program", op)


@mcp.tool()
def flash_verify(image: str, address: int):
    """Verify a binary image against target memory."""
    return call("flash_verify", lambda: jlink.verify(image, address))


@mcp.tool()
def flash_erase(confirmation: str):
    """Erase internal device flash. Requires ERASE_INTERNAL_FLASH confirmation."""
    def op():
        if cfg.safety.require_erase_confirmation and confirmation != "ERASE_INTERNAL_FLASH":
            raise MCPError("Explicit confirmation required", "SAFETY_CONFIRMATION_REQUIRED")
        return jlink.erase()
    return call("flash_erase", op)


@mcp.tool()
def external_flash_info():
    """Return configured XSPI/OctoSPI external flash information."""
    e = cfg.external_flash
    return ok("external_flash_info", {
        "enabled": e.enabled,
        "controller": e.controller,
        "mapped_address": f"0x{e.mapped_address:08X}",
        "size": e.size,
        "expected_jedec_id": e.jedec_id,
    })


@mcp.tool()
def external_flash_read(offset: int = 0, length: int = 64):
    """Read memory-mapped external flash."""
    address = cfg.external_flash.mapped_address + offset
    return call("external_flash_read", lambda: jlink.read_memory(address, length))


@mcp.tool()
def external_flash_test():
    """Perform a non-destructive read test of external flash mapping."""
    def op():
        address = cfg.external_flash.mapped_address
        sample = jlink.read_memory(address, 16)
        return {
            "controller": cfg.external_flash.controller,
            "mapped_address": f"0x{address:08X}",
            "read_test": "PASS" if len(sample["data_hex"]) == 32 else "FAILED",
            "sample": sample,
        }
    return call("external_flash_test", op)


def _gdb_start(elf: str | None = None):
    global gdb_server, gdb
    if gdb_server is None or gdb_server.poll() is not None:
        exe = jlink.runner.resolve(cfg.executables.gdb_server)
        args = [
            exe,
            "-device", cfg.target.device,
            "-if", cfg.target.interface,
            "-speed", str(cfg.target.speed_khz),
            "-port", str(cfg.debug.gdb_port),
        ]
        if cfg.target.jlink_serial is not None:
            args += ["-select", str(cfg.target.jlink_serial)]
        gdb_server = subprocess.Popen(
            args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True
        )
        time.sleep(cfg.debug.gdb_startup_timeout_s)
        if gdb_server.poll() is not None:
            raise MCPError("J-Link GDB Server failed to start", "GDB_SERVER_FAILED")

    if gdb is None:
        gdb_exe = jlink.runner.resolve(cfg.executables.gdb)
        gdb = GdbController(
            command=[gdb_exe, "--interpreter=mi3"],
            time_to_check_for_additional_output_sec=0.2,
        )
        gdb.write(f"target extended-remote :{cfg.debug.gdb_port}",
                  timeout_sec=cfg.debug.gdb_command_timeout_s)

    if elf:
        symbols.load(elf)
        gdb.write(f'-file-exec-and-symbols "{elf}"',
                  timeout_sec=cfg.debug.gdb_command_timeout_s)

    return {"gdb_port": cfg.debug.gdb_port, "elf": elf}


def _gdb_require():
    if gdb is None:
        raise MCPError("GDB session is not running", "GDB_NOT_RUNNING")
    return gdb


@mcp.tool()
def debug_start(elf: str | None = None):
    """Start J-Link GDB Server and connect GDB."""
    return call("debug_start", lambda: _gdb_start(elf))


@mcp.tool()
def debug_stop():
    """Stop the managed GDB and J-Link GDB Server processes."""
    global gdb_server, gdb
    def op():
        global gdb_server, gdb
        if gdb:
            try:
                gdb.exit()
            except Exception:
                pass
            gdb = None
        if gdb_server and gdb_server.poll() is None:
            gdb_server.terminate()
            try:
                gdb_server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                gdb_server.kill()
        gdb_server = None
        return {"stopped": True}
    return call("debug_stop", op)


def _gdb_command(command: str):
    return _gdb_require().write(
        command, timeout_sec=cfg.debug.gdb_command_timeout_s
    )


@mcp.tool()
def debug_continue():
    """Continue target execution through GDB."""
    return call("debug_continue", lambda: {"responses": _gdb_command("-exec-continue")})


@mcp.tool()
def debug_pause():
    """Interrupt target execution through GDB."""
    return call("debug_pause", lambda: {"responses": _gdb_command("-exec-interrupt")})


@mcp.tool()
def debug_step():
    """Single-step through GDB."""
    return call("debug_step", lambda: {"responses": _gdb_command("-exec-step")})


@mcp.tool()
def debug_breakpoint_set(location: str):
    """Set a breakpoint by address, symbol, or source location."""
    return call("debug_breakpoint_set",
                lambda: {"responses": _gdb_command(f'-break-insert "{location}"')})


@mcp.tool()
def debug_breakpoint_clear(number: str):
    """Clear a GDB breakpoint number."""
    return call("debug_breakpoint_clear",
                lambda: {"responses": _gdb_command(f"-break-delete {number}")})


@mcp.tool()
def debug_backtrace():
    """Return the current GDB stack frames."""
    return call("debug_backtrace",
                lambda: {"responses": _gdb_command("-stack-list-frames")})


@mcp.tool()
def read_variable(name: str):
    """Evaluate a variable or GDB expression."""
    return call("read_variable",
                lambda: {"responses": _gdb_command(f'-data-evaluate-expression "{name}"')})


@mcp.tool()
def stm32_fault_info():
    """Read and decode Cortex-M fault status registers."""
    def op():
        addresses = {
            "SHCSR": 0xE000ED24, "CFSR": 0xE000ED28,
            "HFSR": 0xE000ED2C, "DFSR": 0xE000ED30,
            "MMFAR": 0xE000ED34, "BFAR": 0xE000ED38,
            "AFSR": 0xE000ED3C, "ICSR": 0xE000ED04,
        }
        values = {}
        for name, address in addresses.items():
            raw = bytes.fromhex(jlink.read_memory(address, 4)["data_hex"])
            values[name] = int.from_bytes(raw, "little") if len(raw) == 4 else None
        cfsr = values["CFSR"] or 0
        hfsr = values["HFSR"] or 0
        return {
            "registers": {
                k: (f"0x{v:08X}" if v is not None else "unavailable")
                for k, v in values.items()
            },
            "decoded": {
                "hard_fault_forced_or_debug": bool(hfsr & 0x40000000),
                "memmanage_fault": bool(cfsr & 0x000000FF),
                "bus_fault": bool(cfsr & 0x0000FF00),
                "usage_fault": bool(cfsr & 0xFFFF0000),
                "busfault_precise": bool(cfsr & (1 << 9)),
                "busfault_bfar_valid": bool(cfsr & (1 << 15)),
            },
        }
    return call("stm32_fault_info", op)


@mcp.tool()
def boot_diagnose():
    """Collect target state and Cortex-M fault evidence for boot troubleshooting."""
    return call("boot_diagnose", lambda: {
        "target": jlink.status(),
        "fault": stm32_fault_info(),
        "external_flash_config": {
            "controller": cfg.external_flash.controller,
            "mapped_address": f"0x{cfg.external_flash.mapped_address:08X}",
        },
        "note": "This is an evidence report; it does not claim undocumented boot-ROM behavior.",
    })


@mcp.tool()
def load_symbols(elf: str):
    """Load ELF symbols for address and symbol resolution."""
    return call("load_symbols", lambda: symbols.load(elf))


@mcp.tool()
def resolve_symbol(name: str):
    """Resolve an ELF symbol to an address."""
    return call("resolve_symbol", lambda: symbols.symbol(name))


@mcp.tool()
def resolve_address(address: int):
    """Resolve an address to the nearest loaded ELF symbol."""
    return call("resolve_address", lambda: symbols.address(address))


@mcp.tool()
def jlink_command(command: str):
    """Run one raw J-Link Commander command; use semantic tools whenever possible."""
    def op():
        if not cfg.safety.allow_raw_jlink_command:
            raise MCPError("Raw J-Link command is disabled", "RAW_COMMAND_DISABLED")
        return {"output": jlink.raw(command)}
    return call("jlink_command", op)


def main():
    mcp.run(transport="stdio")
