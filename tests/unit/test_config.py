import pytest
from stm32_jlink_mcp.config import Config


def test_raw_commands_default_disabled():
    assert Config().safety.allow_raw_jlink_command is False
