from stm32_jlink_mcp.core import parse_mem8


def test_parse_mem8():
    text = """
    08000000: 01 02 03 04 05 06 07 08  ........
    """
    assert parse_mem8(text, 8) == bytes(range(1, 9))
