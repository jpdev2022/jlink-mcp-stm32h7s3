# Architecture

J-Link remains the low-level debug engine. MCP is the AI-native abstraction layer.

```text
Claude/Codex/Hermes
        |
       MCP
        |
STM32 J-Link MCP
  |     |      |
J-Link  GDB   ELF/DWARF
  |
 SWD
  |
STM32H7S3
  |
XSPI/OctoSPI
  |
NOR flash
```

## Responsibilities

### J-Link

- SWD
- target connection
- flash algorithms
- GDB remote transport
- low-level memory/register access

### MCP

- semantic tool API
- target/session state
- safety
- error normalization
- STM32 fault decoding
- external-flash abstraction
- ELF symbol resolution
- AI-friendly results

### AI

- source reasoning
- debugging strategy
- code changes
- build/test iteration
