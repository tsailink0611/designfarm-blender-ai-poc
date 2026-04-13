import pytest
from src.parser.instruction_parser import InstructionParser
from src.parser.schema import LayoutSpec


@pytest.fixture
def parser():
    return InstructionParser()


def test_parse_dimensions(parser):
    text = "6m×8mの展示ブース"
    spec = parser.parse(text)
    assert spec.width == 6.0
    assert spec.depth == 8.0


def test_parse_dimensions_alternate_format(parser):
    text = "幅10m奥行き12mのブース"
    spec = parser.parse(text)
    assert spec.width == 10.0
    assert spec.depth == 12.0


def test_parse_counter_count(parser):
    text = "受付カウンター2つ"
    spec = parser.parse(text)
    assert len(spec.counters) == 2


def test_parse_panel_count(parser):
    text = "壁面パネル3面"
    spec = parser.parse(text)
    assert len(spec.panels) == 3


def test_parse_monitor_count(parser):
    text = "モニター2台"
    spec = parser.parse(text)
    assert len(spec.monitors) == 2


def test_parse_circulation(parser):
    text = "右回り導線"
    spec = parser.parse(text)
    assert spec.circulation == "clockwise"


def test_parse_circulation_left(parser):
    text = "左回り動線"
    spec = parser.parse(text)
    assert spec.circulation == "counterclockwise"


def test_parse_style_white_wood(parser):
    text = "白基調で木目アクセント"
    spec = parser.parse(text)
    assert spec.style == "white_wood"


def test_parse_fallback_on_empty(parser):
    spec = parser.parse("")
    assert isinstance(spec, LayoutSpec)
    assert spec.width == 6.0


def test_parse_full_example(parser):
    text = "6m×8mの展示ブース。受付カウンター1つ。壁面パネル3面。モニター2台。右回り導線。白基調で木目アクセント。"
    spec = parser.parse(text)
    assert spec.width == 6.0
    assert spec.depth == 8.0
    assert len(spec.counters) == 1
    assert len(spec.panels) == 3
    assert len(spec.monitors) == 2
    assert spec.circulation == "clockwise"
    assert spec.style == "white_wood"


def test_cameras_always_generated(parser):
    spec = parser.parse("テストブース")
    assert len(spec.cameras) == 2
    types = {c.type for c in spec.cameras}
    assert "top_view" in types
    assert "visitor_view" in types
