from pathlib import Path

from stm32_jlink_mcp.svd import SvdDatabase


def test_svd_parser(tmp_path: Path):
    svd = tmp_path / "test.svd"
    svd.write_text(
        """<device><name>TEST</name><peripherals><peripheral>"
        "<name>FOO</name><baseAddress>0x40000000</baseAddress><description>Foo</description>"
        "<registers><register><name>CR</name><addressOffset>0x10</addressOffset>"
        "<size>32</size><access>read-write</access><fields>"
        "<field><name>EN</name><bitOffset>0</bitOffset><bitWidth>1</bitWidth></field>"
        "</fields></register></registers></peripheral></peripherals></device>""",
        encoding="utf-8",
    )
    db = SvdDatabase()
    result = db.load(str(svd))
    assert result["device"] == "TEST"
    info = db.register_info("FOO", "CR")
    assert info["address"] == "0x40000010"
    assert info["fields"][0]["name"] == "EN"
