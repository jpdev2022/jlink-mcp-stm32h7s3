import pytest

from stm32_jlink_mcp.config import Config
from stm32_jlink_mcp.errors import MCPError
from stm32_jlink_mcp.safety.policy import SafetyPolicy


def test_read_only_denies_writes():
    policy = SafetyPolicy(Config.model_validate({"safety": {"mode": "read_only"}}))
    with pytest.raises(MCPError) as exc:
        policy.require_read_write_mode("memory_write")
    assert exc.value.code == "READ_ONLY_MODE"


def test_confirmation_is_exact():
    policy = SafetyPolicy(Config())
    with pytest.raises(MCPError) as exc:
        policy.require_confirmation("yes", "ERASE_INTERNAL_FLASH")
    assert exc.value.code == "SAFETY_CONFIRMATION_REQUIRED"


def test_limits():
    policy = SafetyPolicy(Config())
    policy.check_read_length(1024)
    with pytest.raises(MCPError):
        policy.check_read_length(Config().safety.max_memory_read_bytes + 1)
