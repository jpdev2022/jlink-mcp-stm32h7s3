from stm32_jlink_mcp.config import Config
from stm32_jlink_mcp.targets.stm32h7s3 import STM32H7S3I8_PROFILE


def test_stm32h7s3i8_board_profile_defaults():
    cfg = Config()
    assert cfg.target.device == "STM32H7S3I8T6"
    assert cfg.target.jlink_device == "STM32H7S3I8"
    assert cfg.target.package == "LQFP176"
    assert cfg.external_flash.controller == "XSPI1"
    assert cfg.external_flash.mapped_address == 0x90000000
    assert cfg.external_flash.size == 64 * 1024 * 1024
    assert cfg.external_flash.part_number == "MX25UW51245GXDI00"
    assert cfg.external_flash.jedec_id == "C2 81 3A"
    assert cfg.external_flash.hal_memory_size == "HAL_XSPI_SIZE_512MB"


def test_memory_profile_has_rm0477_h7s3_windows():
    assert STM32H7S3I8_PROFILE.region_for(0x0002FFFF).name == "itcm"
    assert STM32H7S3I8_PROFILE.region_for(0x0800FFFF).name == "user_flash"
    assert STM32H7S3I8_PROFILE.region_for(0x1FF1FFFF).name == "system_flash"
    assert STM32H7S3I8_PROFILE.region_for(0x2002FFFF).name == "dtcm_ram"
    assert STM32H7S3I8_PROFILE.region_for(0x24071FFF).name == "axi_sram"
    assert STM32H7S3I8_PROFILE.region_for(0x90000000).name == "xspi1_window"


def test_external_flash_geometry_is_validated():
    from pydantic import ValidationError
    from stm32_jlink_mcp.config import ExternalFlashConfig

    try:
        ExternalFlashConfig(controller="XSPI1", mapped_address=0x70000000)
    except ValidationError:
        pass
    else:
        raise AssertionError("XSPI1 must not accept the XSPI2 mapped address")
