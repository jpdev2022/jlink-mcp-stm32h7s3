import pytest

from stm32_jlink_mcp.option_bytes import (
    OptionByteWriteRequest,
    validate_mass_erase,
    validate_write,
)


def test_option_byte_write_requires_confirmation():
    with pytest.raises(ValueError):
        validate_write(
            OptionByteWriteRequest("FLASH_OPTSR_PRG", 0, "WRONG")
        )


def test_option_byte_write_rejects_current_register():
    with pytest.raises(ValueError):
        validate_write(
            OptionByteWriteRequest("FLASH_OPTSR_CUR", 0, "PROGRAM_OPTION_BYTES")
        )


def test_option_byte_write_accepts_programming_register():
    validate_write(
        OptionByteWriteRequest("FLASH_OPTSR_PRG", 0xFFFFFFFF, "PROGRAM_OPTION_BYTES")
    )


def test_mass_erase_requires_explicit_confirmation():
    with pytest.raises(ValueError):
        validate_mass_erase("ERASE_INTERNAL_FLASH")

    validate_mass_erase("MASS_ERASE_INTERNAL_FLASH")
