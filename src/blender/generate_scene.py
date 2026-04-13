"""
Blenderシーン生成メインモジュール
LayoutSpec JSONを受け取り、シーンを構築してPNGを2枚出力する
このスクリプトはBlenderの--pythonオプション経由で実行する

実行方法:
    blender --background --python src/blender/generate_scene.py -- path/to/layout.json

注意: このモジュールはBlender内部Pythonで動作するため、pydanticに依存しない
"""
from __future__ import annotations
import json
import sys
import math
import logging
from pathlib import Path

import bpy

# プロジェクトルートをPYTHONPATHに追加（src/utils等のインポートのため）
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.blender.primitives import (
    clear_scene, add_floor, add_wall,
    add_counter, add_panel, add_monitor
)
from src.blender.materials import apply_materials_to_scene
from src.blender.camera_setup import setup_cameras, render_from_camera
from src.utils.paths import resolve_output_dir, blender_safe_path

logger = logging.getLogger(__name__)


def _add_ambient_light(width: float, depth: float, height: float) -> None:
    """シーン全体を照らすエリアライトを追加する"""
    bpy.ops.object.light_add(type='AREA', location=(width / 2, depth / 2, height + 1.5))
    light = bpy.context.active_object
    light.name = "AmbientLight"
    light.data.energy = 500
    light.data.size = max(width, depth) * 0.8


def _build_default_walls(width: float, depth: float, height: float) -> None:
    """wallsが空の場合、部屋の4壁を自動生成する"""
    t = 0.1
    walls = [
        dict(wall_id="back",  position=[width/2, depth, height/2], rotation_z=0.0,                 width=width, height=height, thickness=t),
        dict(wall_id="front", position=[width/2, 0,     height/2], rotation_z=0.0,                 width=width, height=height, thickness=t),
        dict(wall_id="left",  position=[0,       depth/2, height/2], rotation_z=math.radians(90),  width=depth, height=height, thickness=t),
        dict(wall_id="right", position=[width,   depth/2, height/2], rotation_z=math.radians(90),  width=depth, height=height, thickness=t),
    ]
    for wall in walls:
        add_wall(**wall)


def generate_scene(spec: dict) -> list[str]:
    """
    LayoutSpec dictからBlenderシーンを構築し、PNG2枚を出力する
    pydanticを使わず、生のdictで動作する
    """
    width  = float(spec.get("width",  6.0))
    depth  = float(spec.get("depth",  8.0))
    height = float(spec.get("height", 2.7))
    style  = spec.get("style", "white_wood")
    render_cfg = spec.get("render", {})

    logger.info(f"シーン生成開始: {width}m x {depth}m")

    clear_scene()

    # 床
    add_floor(width, depth)

    # 壁（仕様にあれば使用、なければ自動生成）
    walls = spec.get("walls", [])
    if walls:
        for w in walls:
            add_wall(
                wall_id=w["id"],
                position=w.get("position", [0.0, 0.0, 0.0]),
                rotation_z=float(w.get("rotation_z", 0.0)),
                width=float(w.get("width", 6.0)),
                height=float(w.get("height", 2.7)),
                thickness=float(w.get("thickness", 0.1)),
                material_name=w.get("material", "white_plaster"),
            )
    else:
        _build_default_walls(width, depth, height)

    # カウンター
    for c in spec.get("counters", []):
        add_counter(
            counter_id=c["id"],
            position=c.get("position", [0.0, 0.0, 0.0]),
            rotation_z=float(c.get("rotation_z", 0.0)),
            width=float(c.get("width", 1.5)),
            depth=float(c.get("depth", 0.6)),
            height=float(c.get("height", 0.9)),
            material_name=c.get("material", "wood_accent"),
        )

    # パネル
    for p in spec.get("panels", []):
        add_panel(
            panel_id=p["id"],
            position=p.get("position", [0.0, 0.0, 0.0]),
            rotation_z=float(p.get("rotation_z", 0.0)),
            width=float(p.get("width", 1.0)),
            height=float(p.get("height", 2.4)),
            thickness=float(p.get("thickness", 0.05)),
            material_name=p.get("material", "white_plaster"),
        )

    # モニター
    for m in spec.get("monitors", []):
        add_monitor(
            monitor_id=m["id"],
            position=m.get("position", [0.0, 0.0, 0.0]),
            rotation_z=float(m.get("rotation_z", 0.0)),
            width=float(m.get("width", 0.8)),
            height=float(m.get("height", 0.5)),
            depth=float(m.get("depth", 0.05)),
            material_name=m.get("material", "dark_screen"),
        )

    # ライト
    _add_ambient_light(width, depth, height)

    # マテリアル適用
    apply_materials_to_scene(style)

    # カメラ配置・レンダリング
    output_dir = resolve_output_dir(spec.get("render_output_dir", "./output"))
    cam_objects = setup_cameras(spec.get("cameras", []), width, depth, height)

    resolution_x = int(render_cfg.get("resolution_x", 1280))
    resolution_y = int(render_cfg.get("resolution_y", 720))
    engine       = render_cfg.get("engine", "CYCLES")
    samples      = int(render_cfg.get("samples", 64))

    output_paths = []
    for cam_id, cam_obj in cam_objects.items():
        output_path = blender_safe_path(output_dir / f"{cam_id}.png")
        logger.info(f"レンダリング中: {cam_id} -> {output_path}")
        render_from_camera(
            cam_obj=cam_obj,
            output_path=output_path,
            resolution_x=resolution_x,
            resolution_y=resolution_y,
            engine=engine,
            samples=samples,
        )
        output_paths.append(output_path)

    logger.info(f"完了: {len(output_paths)}枚のPNGを生成しました")
    return output_paths


def main() -> None:
    """
    コマンドライン引数からJSONファイルパスを受け取り、シーン生成を実行する
    使用方法: blender --background --python generate_scene.py -- path/to/layout.json
    """
    argv = sys.argv
    args = argv[argv.index("--") + 1:] if "--" in argv else []

    if not args:
        print("エラー: JSONファイルパスを指定してください", file=sys.stderr)
        print("使用方法: blender --background --python generate_scene.py -- layout.json", file=sys.stderr)
        sys.exit(1)

    json_path = Path(args[0])
    if not json_path.exists():
        print(f"エラー: ファイルが見つかりません: {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        spec = json.load(f)

    output_paths = generate_scene(spec)
    print(f"生成完了: {', '.join(output_paths)}")


if __name__ == "__main__":
    main()
