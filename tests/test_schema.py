import pytest
from src.parser.schema import LayoutSpec, Wall, Counter, Panel, Monitor, Camera, RenderConfig


def test_default_layout_spec():
    spec = LayoutSpec()
    assert spec.width == 6.0
    assert spec.depth == 8.0
    assert spec.height == 2.7
    assert spec.style == "white_wood"
    assert isinstance(spec.walls, list)


def test_layout_spec_from_dict():
    data = {
        "width": 10.0,
        "depth": 12.0,
        "height": 3.0,
        "style": "modern",
        "circulation": "clockwise",
        "walls": [{"id": "w1", "position": [0, 0, 0], "rotation_z": 0.0, "width": 10.0, "height": 3.0}],
        "counters": [],
        "panels": [],
        "monitors": [],
        "cameras": [],
        "render_output_dir": "./output"
    }
    spec = LayoutSpec(**data)
    assert spec.width == 10.0
    assert len(spec.walls) == 1


def test_wall_defaults():
    wall = Wall(id="w1", position=[0, 0, 0])
    assert wall.width == 6.0
    assert wall.height == 2.7
    assert wall.thickness == 0.1


def test_counter_defaults():
    counter = Counter(id="c1", position=[1.0, 0.5, 0.0])
    assert counter.width == 1.5
    assert counter.depth == 0.6
    assert counter.height == 0.9


def test_camera_types():
    cam_top = Camera(id="cam_top", type="top_view")
    cam_visitor = Camera(id="cam_visitor", type="visitor_view")
    assert cam_top.type == "top_view"
    assert cam_visitor.type == "visitor_view"
