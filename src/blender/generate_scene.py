"""
Blenderシーン生成メインモジュール
LayoutSpecを受け取り、シーンを構築してPNGを2枚出力する
このスクリプトはBlenderの--pythonオプション経由で実行する

実行方法:
    blender --background --python src/blender/generate_scene.py -- path/to/layout.json
"""
from __future__ import annotations
import json
import sys
import math
from pathlib import Path

import bpy

# srcディレクトリをPYTHONPATHに追加（Blender内からインポートするため）
_src_dir = str(Path(__file__).resolve().parent.parent.parent)
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from src.parser.schema import LayoutSpec
from src.blender.primitives import (
    clear_scene, add_floor, add_wall,
    add_counter, add_panel, add_monitor
)
from src.blender.materials import apply_materials_to_scene
from src.blender.camera_setup import setup_cameras, render_from_camera
from src.utils.paths import resolve_output_dir, blender_safe_path
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _add_ambient_light(width: float, depth: float, height: float) -> None:
    """シーン全体を照らすエリアライトを追加する"""
    bpy.ops.object.light_add(type='AREA', location=(width / 2, depth / 2, height + 1.5))
    light = bpy.context.active_object
    light.name = "AmbientLight"
    light.data.energy = 500
    light.data.size = max(width, depth) * 0.8


def _build_default_walls(spec: LayoutSpec) -> None:
    """LayoutSpecにwallsが空の場合、部屋の4壁を自動生成する"""
    w, d, h = spec.width, spec.depth, spec.height
    t = 0.1
    walls = [
        # 奥壁
        dict(wall_id="back",   position=[w/2, d, h/2], rotation_z=0.0,                width=w, height=h, thickness=t),
        # 手前壁
        dict(wall_id="front",  position=[w/2, 0, h/2], rotation_z=0.0,                width=w, height=h, thickness=t),
        # 左壁
        dict(wall_id="left",   position=[0, d/2, h/2], rotation_z=math.radians(90),   width=d, height=h, thickness=t),
        # 右壁
        dict(wall_id="right",  position=[w, d/2, h/2], rotation_z=math.radians(90),   width=d, height=h, thickness=t),
    ]
    for wall in walls:
        add_wall(**wall)


def generate_scene(spec: LayoutSpec) -> list[str]:
    """
    LayoutSpecからBlenderシーンを構築し、PNG2枚を出力する
    Returns: 生成されたPNGファイルパスのリスト
    """
    logger.info(f"シーン生成開始: {spec.width}m x {spec.depth}m")

    clear_scene()

    # 床
    add_floor(spec.width, spec.depth)

    # 壁（仕様にあれば使用、なければ自動生成）
    if spec.walls:
        for wall in spec.walls:
            add_wall(
                wall_id=wall.id,
                position=wall.position,
                rotation_z=wall.rotation_z,
                width=wall.width,
                height=wall.height,
                thickness=wall.thickness,
                material_name=wall.material
            )
    else:
        _build_default_walls(spec)

    # カウンター
    for counter in spec.counters:
        add_counter(
            counter_id=counter.id,
            position=counter.position,
            rotation_z=counter.rotation_z,
            width=counter.width,
            depth=counter.depth,
            height=counter.height,
            material_name=counter.material
        )

    # パネル
    for panel in spec.panels:
        add_panel(
            panel_id=panel.id,
            position=panel.position,
            rotation_z=panel.rotation_z,
            width=panel.width,
            height=panel.height,
            thickness=panel.thickness,
            material_name=panel.material
        )

    # モニター
    for monitor in spec.monitors:
        add_monitor(
            monitor_id=monitor.id,
            position=monitor.position,
            rotation_z=monitor.rotation_z,
            width=monitor.width,
            height=monitor.height,
            depth=monitor.depth,
            material_name=monitor.material
        )

    # ライト
    _add_ambient_light(spec.width, spec.depth, spec.height)

    # マテリアル適用
    apply_materials_to_scene(spec.style)

    # カメラ配置・レンダリング
    output_dir = resolve_output_dir(spec.render_output_dir)
    cam_objects = setup_cameras(spec.cameras, spec.width, spec.depth, spec.height)

    output_paths = []
    for cam_id, cam_obj in cam_objects.items():
        output_path = blender_safe_path(output_dir / f"{cam_id}.png")
        logger.info(f"レンダリング中: {cam_id} -> {output_path}")
        render_from_camera(
            cam_obj=cam_obj,
            output_path=output_path,
            resolution_x=spec.render.resolution_x,
            resolution_y=spec.render.resolution_y,
            engine=spec.render.engine,
            samples=spec.render.samples
        )
        output_paths.append(output_path)

    logger.info(f"完了: {len(output_paths)}枚のPNGを生成しました")
    return output_paths


def main() -> None:
    """
    コマンドライン引数からJSONファイルパスを受け取り、シーン生成を実行する
    使用方法: blender --background --python generate_scene.py -- path/to/layout.json
    """
    # Blenderの引数区切り「--」以降を取得
    argv = sys.argv
    if "--" in argv:
        args = argv[argv.index("--") + 1:]
    else:
        args = []

    if not args:
        print("エラー: JSONファイルパスを指定してください", file=sys.stderr)
        print("使用方法: blender --background --python generate_scene.py -- layout.json", file=sys.stderr)
        sys.exit(1)

    json_path = Path(args[0])
    if not json_path.exists():
        print(f"エラー: ファイルが見つかりません: {json_path}", file=sys.stderr)
        sys.exit(1)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    spec = LayoutSpec(**data)
    output_paths = generate_scene(spec)
    print(f"生成完了: {', '.join(output_paths)}")


if __name__ == "__main__":
    main()
