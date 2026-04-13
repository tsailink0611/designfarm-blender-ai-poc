"""
カメラ設定モジュール
俯瞰視点・来場者視点の2カメラを生成・配置する
"""
from __future__ import annotations
import math
import bpy
from src.parser.schema import Camera as CameraSpec


def add_camera(spec: CameraSpec) -> bpy.types.Object:
    """CameraSpecに基づいてBlenderカメラを生成する"""
    bpy.ops.object.camera_add()
    cam_obj = bpy.context.active_object
    cam_obj.name = f"Camera_{spec.id}"
    cam_obj.data.lens = spec.focal_length

    if spec.location:
        cam_obj.location = tuple(spec.location)
    if spec.rotation:
        cam_obj.rotation_euler = tuple(spec.rotation)

    return cam_obj


def setup_cameras(
    camera_specs: list[CameraSpec],
    width: float,
    depth: float,
    height: float
) -> dict[str, bpy.types.Object]:
    """
    カメラリストをBlenderシーンに配置する
    locationが未指定の場合はtype別にデフォルト位置を計算する
    """
    cam_objects: dict[str, bpy.types.Object] = {}

    for spec in camera_specs:
        filled = _fill_camera_defaults(spec, width, depth, height)
        cam_obj = add_camera(filled)
        cam_objects[spec.id] = cam_obj

    return cam_objects


def _fill_camera_defaults(
    spec: CameraSpec,
    width: float,
    depth: float,
    height: float
) -> CameraSpec:
    """locationが未指定のカメラにデフォルト値を補完する"""
    if spec.location is not None and spec.rotation is not None:
        return spec

    if spec.type == "top_view":
        elevation = max(width, depth) * 1.3
        location = [width / 2, depth / 2, elevation]
        rotation = [0.0, 0.0, 0.0]
    else:  # visitor_view
        location = [width / 2, -2.5, 1.7]
        rotation = [math.radians(75), 0.0, 0.0]

    return spec.model_copy(update={
        "location": spec.location or location,
        "rotation": spec.rotation or rotation,
    })


def render_from_camera(
    cam_obj: bpy.types.Object,
    output_path: str,
    resolution_x: int = 1280,
    resolution_y: int = 720,
    engine: str = "CYCLES",
    samples: int = 64
) -> None:
    """指定カメラでレンダリングしてPNGに保存する"""
    scene = bpy.context.scene
    scene.camera = cam_obj
    scene.render.engine = engine
    scene.render.resolution_x = resolution_x
    scene.render.resolution_y = resolution_y
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = output_path

    if engine == "CYCLES":
        scene.cycles.samples = samples

    bpy.ops.render.render(write_still=True)
