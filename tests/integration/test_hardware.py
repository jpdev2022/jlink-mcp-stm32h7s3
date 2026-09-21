import os

import pytest


@pytest.mark.hardware
@pytest.mark.skipif(os.getenv("STM32_JLINK_MCP_HARDWARE_TEST") != "1", reason="hardware not enabled")
def test_hardware_placeholder():
    """Reserved for a real self-hosted J-Link + STM32H7S3 test fixture."""
    pytest.fail("Configure the physical hardware fixture before enabling this test suite")
