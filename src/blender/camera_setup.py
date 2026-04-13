"""
カメラ設定モジュール
俯瞰視点・来場者視点の2カメラを生成・配置する

注意: このモジュールはBlender内部Pythonで動作するため、pydanticに依存しない
カメラ仕様はdictで受け取る（LayoutSpec.cameras の各要素と同じ構造）
"""
from __future__ import annotations
import math
import bpy


def add_camera(spec: dict) -> bpy.types.Object:
    """
    カメラ仕様dict（id/type/location/rotation/focal_length）に基づいてBlenderカメラを生成する
    """
    bpy.ops.object.camera_add()
    cam_obj = bpy.context.active_object
    cam_obj.name = f"Camera_{spec['id']}"
    cam_obj.data.lens = float(spec.get("focal_length", 35.0))

    location = spec.get("location")
    rotation = spec.get("rotation")

    if location:
        cam_obj.location = tuple(float(v) for v in location)
    if rotation:
        cam_obj.rotation_euler = tuple(float(v) for v in rotation)

    return cam_obj


def setup_cameras(
    camera_specs: list[dict],
    width: float,
    depth: float,
    height: float,
) -> dict[str, bpy.types.Object]:
    """
    カメラdictリストをBlenderシーンに配置する
    locationが未指定の場合はtype別にデフォルト位置を計算する
    """
    cam_objects: dict[str, bpy.types.Object] = {}

    # カメラ仕様がなければデフォルト2視点を生成
    if not camera_specs:
        camera_specs = _default_camera_specs(width, depth, height)

    for spec in camera_specs:
        filled = _fill_camera_defaults(spec, width, depth, height)
        cam_obj = add_camera(filled)
        cam_objects[spec["id"]] = cam_obj

    return cam_objects


def _default_camera_specs(width: float, depth: float, height: float) -> list[dict]:
    """カメラ仕様が未指定の場合のデフォルト2視点"""
    return [
        {
            "id": "cam_top",
            "type": "top_view",
            "location": [width / 2, depth / 2, max(width, depth) * 1.3],
            "rotation": [0.0, 0.0, 0.0],
            "focal_length": 50.0,
        },
        {
            "id": "cam_visitor",
            "type": "visitor_view",
            "location": [width / 2, -2.5, 1.7],
            "rotation": [math.radians(75), 0.0, 0.0],
            "focal_length": 35.0,
        },
    ]


def _fill_camera_defaults(spec: dict, width: float, depth: float, height: float) -> dict:
    """locationが未指定のカメラにデフォルト値を補完する"""
    if spec.get("location") is not None and spec.get("rotation") is not None:
        return spec

    cam_type = spec.get("type", "visitor_view")
    if cam_type == "top_view":
        default_location = [width / 2, depth / 2, max(width, depth) * 1.3]
        default_rotation = [0.0, 0.0, 0.0]
    else:
        default_location = [width / 2, -2.5, 1.7]
        default_rotation = [math.radians(75), 0.0, 0.0]

    return {
        **spec,
        "location": spec.get("location") or default_location,
        "rotation": spec.get("rotation") or default_rotation,
    }


def render_from_camera(
    cam_obj: bpy.types.Object,
    output_path: str,
    resolution_x: int = 1280,
    resolution_y: int = 720,
    engine: str = "CYCLES",
    samples: int = 64,
) -> None:
    """指定カメラでレンダリングしてPNGに保存する"""
    scene = bpy.context.scene
    scene.camera = cam_obj
    scene.render.engine = engine
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = output_path

    if engine == "CYCLES":
        scene.cycles.samples = samples

    bpy.ops.render.render(write_still=True)
