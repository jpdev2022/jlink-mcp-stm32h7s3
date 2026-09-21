from stm32_jlink_mcp.targets import STM32H7S3_PROFILE


def test_h7s3_xspi_windows():
    assert STM32H7S3_PROFILE.region_for(0x70000000, 4).name == "xspi2_window"
    assert STM32H7S3_PROFILE.region_for(0x90000000, 4).name == "xspi1_window"


def test_h7s3_internal_regions():
    assert STM32H7S3_PROFILE.region_for(0x20000000, 4).name == "dtcm_ram"
    assert STM32H7S3_PROFILE.region_for(0x24000000, 4).name == "axi_sram"
