from stm32_jlink_mcp.probe.jlink import parse_mem8


def test_parse_mem8_ignores_ascii_column():
    output = """
00000000 = 00 11 22 33 44 55 66 77  ABCDEFGH
00000008 = 88 99 AA BB CC DD EE FF  ........
"""
    assert parse_mem8(output, 16) == bytes.fromhex("00112233445566778899aabbccddeeff")


def test_parse_mem8_truncates_to_expected_length():
    output = "00000000 = 00 01 02 03 04 05 06 07"
    assert parse_mem8(output, 3) == bytes.fromhex("000102")
