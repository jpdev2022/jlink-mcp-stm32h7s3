# Claude Code / MCP Host Integration

## Local stdio configuration

After installing the package in a virtual environment, point the MCP host at:

```text
/absolute/path/to/repo/.venv/bin/stm32-jlink-mcp
```

Example conceptual configuration:

```json
{
  "mcpServers": {
    "stm32-jlink": {
      "command": "/absolute/path/to/repo/.venv/bin/stm32-jlink-mcp"
    }
  }
}
```

## Recommended agent workflow

### Inspect a target

```text
probe_list
jlink_connect
target_identify
target_status
stm32_snapshot
```

### Investigate a crash

```text
stm32_fault_info
resolve_address(PC)
diagnose_crash
```

### Debug source code

```text
debug_start(elf)
debug_breakpoint_set("foo.c:123")
debug_continue()
debug_backtrace()
read_variable("state")
```

### Inspect peripheral state

Provide the official STM32H7S3 SVD in configuration, then:

```text
peripheral_info("XSPI2")
register_info("XSPI2", "SR")
register_read("XSPI2", "SR")
```

## Agent safety guidance

Agents should:

1. Identify the target before programming.
2. Prefer `flash_and_verify` or the semantic flash tools over `jlink_command`.
3. Never infer external NOR programming support from `0x70000000` or `0x90000000` alone.
4. Treat `WRITE_MEMORY`, `WRITE_REGISTER`, `PROGRAM_INTERNAL_FLASH`, and `ERASE_INTERNAL_FLASH` as explicit authorization boundaries.
5. Use read-only mode for unattended inspection agents.
