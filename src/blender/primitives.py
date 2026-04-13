"""
Blenderプリミティブ生成モジュール
床・壁・カウンター・パネル・モニター等の基本形状を生成する
bpyはBlender内部でのみ有効なため、このモジュールはBlender経由で実行する
"""
from __future__ import annotations
import math
import bpy


def clear_scene() -> None:
    """既存オブジェクトをすべて削除してシーンを初期化する"""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    # 不要なメッシュデータも削除
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)


def add_floor(width: float, depth: float, material_name: str = "floor_mat") -> bpy.types.Object:
    """床（薄い直方体）を生成する"""
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(width / 2, depth / 2, 0.0))
    obj = bpy.context.active_object
    obj.name = "Floor"
    obj.scale = (width, depth, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    obj["material_slot"] = material_name
    return obj


def add_wall(
    wall_id: str,
    position: list[float],
    rotation_z: float,
    width: float,
    height: float,
    thickness: float,
    material_name: str = "white_plaster"
) -> bpy.types.Object:
    """壁（直方体）を生成する"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=tuple(position))
    obj = bpy.context.active_object
    obj.name = f"Wall_{wall_id}"
    obj.scale = (width, thickness, height)
    obj.rotation_euler[2] = rotation_z
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    obj.location = tuple(position)
    obj["material_slot"] = material_name
    return obj


def add_counter(
    counter_id: str,
    position: list[float],
    rotation_z: float,
    width: float,
    depth: float,
    height: float,
    material_name: str = "wood_accent"
) -> bpy.types.Object:
    """受付カウンター（直方体）を生成する"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(
        position[0], position[1], height / 2
    ))
    obj = bpy.context.active_object
    obj.name = f"Counter_{counter_id}"
    obj.scale = (width, depth, height)
    obj.rotation_euler[2] = rotation_z
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    obj.location = (position[0], position[1], height / 2)
    obj["material_slot"] = material_name
    return obj


def add_panel(
    panel_id: str,
    position: list[float],
    rotation_z: float,
    width: float,
    height: float,
    thickness: float,
    material_name: str = "white_plaster"
) -> bpy.types.Object:
    """壁面パネル（薄い直方体）を生成する"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=tuple(position))
    obj = bpy.context.active_object
    obj.name = f"Panel_{panel_id}"
    obj.scale = (width, thickness, height)
    obj.rotation_euler[2] = rotation_z
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    obj.location = tuple(position)
    obj["material_slot"] = material_name
    return obj


def add_monitor(
    monitor_id: str,
    position: list[float],
    rotation_z: float,
    width: float,
    height: float,
    depth: float,
    material_name: str = "dark_screen"
) -> bpy.types.Object:
    """モニターダミー（薄い直方体）を生成する"""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=tuple(position))
    obj = bpy.context.active_object
    obj.name = f"Monitor_{monitor_id}"
    obj.scale = (width, depth, height)
    obj.rotation_euler[2] = rotation_z
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    obj.location = tuple(position)
    obj["material_slot"] = material_name
    return obj
