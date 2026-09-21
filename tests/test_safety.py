import pytest

from stm32_jlink_mcp.core import Config, MCPError


def test_default_config_has_expected_target():
    cfg = Config()
    assert cfg.target.device == "STM32H7S3L8"


def test_safety_limit():
    cfg = Config()
    with pytest.raises(AssertionError):
        assert 5000 <= cfg.safety.max_memory_write_bytes
