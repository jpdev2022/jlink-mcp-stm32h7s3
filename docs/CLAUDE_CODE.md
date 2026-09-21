# MCP Host Setup

Use the local stdio server.

Example:

```json
{
  "mcpServers": {
    "stm32-jlink": {
      "command": "/absolute/path/to/stm32-jlink-mcp/.venv/bin/stm32-jlink-mcp"
    }
  }
}
```

The AI should normally use semantic tools:

```text
external_flash_test
stm32_fault_info
debug_backtrace
read_variable
flash_program
```

rather than constructing raw J-Link command scripts.

Keep the raw `jlink_command` tool as an escape hatch.
