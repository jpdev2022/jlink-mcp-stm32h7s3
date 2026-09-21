# Development

## Local checks

```bash
python -m compileall -q src tests
PYTHONPATH=src pytest -q tests/unit
ruff check .
```

## Hardware tests

Set:

```bash
export STM32_JLINK_MCP_HARDWARE_TEST=1
```

Then run:

```bash
pytest -m hardware
```

The hardware suite should be expanded only after a dedicated fixture exists. A good fixture has:

- known STM32H7S3L8 target
- dedicated J-Link serial
- known-good firmware image
- known RAM scratch range
- known flash region
- optional external NOR with a documented part number

## Code organization rules

- MCP tool functions should stay thin.
- Put hardware behavior in `service.py` and backend modules.
- Never parse J-Link output inside MCP handlers.
- Never let a tool bypass `DebugSession` for target access.
- Never silently enable destructive operations because a configuration value is missing.
- Keep board-specific behavior out of generic J-Link code.
- Prefer structured evidence over raw terminal output.

## Future milestones

1. Add complete STM32H7S3 CMSIS-SVD handling, including derived peripherals/clusters used by the device SVD.
2. Add richer GDB MI result normalization.
3. Add a board-specific external NOR programmer interface.
4. Add reset-cause decoding from the exact H7S3 SVD/device revision.
5. Add real hardware CI using a self-hosted runner.
6. Add optional SEGGER SDK backend if process-launch overhead becomes material.
