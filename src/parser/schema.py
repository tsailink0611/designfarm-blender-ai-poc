"""
LayoutSpec: Blenderシーン生成のためのJSON仕様スキーマ定義
"""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Wall(BaseModel):
    id: str
    position: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation_z: float = 0.0  # ラジアン
    width: float = 6.0
    height: float = 2.7
    thickness: float = 0.1
    material: str = "white_plaster"


class Counter(BaseModel):
    id: str
    position: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation_z: float = 0.0
    width: float = 1.5
    depth: float = 0.6
    height: float = 0.9
    material: str = "wood_accent"


class Panel(BaseModel):
    id: str
    position: list[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])
    rotation_z: float = 0.0
    width: float = 1.0
    height: float = 2.4
    thickness: float = 0.05
    material: str = "white_plaster"


class Monitor(BaseModel):
    id: str
    position: list[float] = Field(default_factory=lambda: [0.0, 0.0, 1.2])
    rotation_z: float = 0.0
    width: float = 0.8
    height: float = 0.5
    depth: float = 0.05
    material: str = "dark_screen"


class Camera(BaseModel):
    id: str
    type: Literal["top_view", "visitor_view"]
    location: Optional[list[float]] = None  # Noneの場合は自動計算
    rotation: Optional[list[float]] = None  # Noneの場合は自動計算
    focal_length: float = 35.0


class RenderConfig(BaseModel):
    resolution_x: int = 1280
    resolution_y: int = 720
    engine: str = "CYCLES"
    samples: int = 64


class LayoutSpec(BaseModel):
    """展示空間レイアウト仕様 - Blenderシーン生成の入力スキーマ"""
    width: float = 6.0          # 幅(m) X軸
    depth: float = 8.0          # 奥行き(m) Y軸
    height: float = 2.7         # 天井高(m) Z軸
    style: str = "white_wood"   # white_wood / modern / industrial
    circulation: str = "clockwise"  # clockwise / counterclockwise
    walls: list[Wall] = Field(default_factory=list)
    counters: list[Counter] = Field(default_factory=list)
    panels: list[Panel] = Field(default_factory=list)
    monitors: list[Monitor] = Field(default_factory=list)
    cameras: list[Camera] = Field(default_factory=list)
    render_output_dir: str = "./output"
    render: RenderConfig = Field(default_factory=RenderConfig)
