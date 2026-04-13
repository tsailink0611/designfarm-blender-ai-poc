"""
マテリアル定義モジュール
PrincipledBSDFを使ったシンプルなマテリアルを定義する
"""
from __future__ import annotations
import bpy

# スタイル別カラーパレット
STYLE_PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "white_wood": {
        "floor_mat":     (0.85, 0.75, 0.60, 1.0),  # 木目ベージュ
        "white_plaster": (0.95, 0.95, 0.95, 1.0),  # 白壁
        "wood_accent":   (0.55, 0.35, 0.15, 1.0),  # ウッドブラウン
        "dark_screen":   (0.05, 0.05, 0.05, 1.0),  # 黒モニター
    },
    "modern": {
        "floor_mat":     (0.20, 0.20, 0.20, 1.0),  # ダークグレー床
        "white_plaster": (0.90, 0.90, 0.90, 1.0),  # ライトグレー壁
        "wood_accent":   (0.30, 0.30, 0.30, 1.0),  # チャコールグレー
        "dark_screen":   (0.02, 0.02, 0.02, 1.0),
    },
    "industrial": {
        "floor_mat":     (0.40, 0.38, 0.35, 1.0),  # コンクリート調
        "white_plaster": (0.65, 0.63, 0.60, 1.0),  # サンドグレー
        "wood_accent":   (0.45, 0.30, 0.15, 1.0),  # ラスティックブラウン
        "dark_screen":   (0.05, 0.05, 0.05, 1.0),
    },
}


def get_or_create_material(name: str, rgba: tuple[float, float, float, float]) -> bpy.types.Material:
    """名前で既存マテリアルを取得するか新規作成する"""
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.7
        bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def apply_materials_to_scene(style: str) -> None:
    """シーン内の全オブジェクトにスタイル対応マテリアルを適用する"""
    palette = STYLE_PALETTES.get(style, STYLE_PALETTES["white_wood"])

    for mat_name, rgba in palette.items():
        get_or_create_material(mat_name, rgba)

    for obj in bpy.data.objects:
        slot_name = obj.get("material_slot")
        if slot_name and slot_name in bpy.data.materials:
            mat = bpy.data.materials[slot_name]
            if obj.data and hasattr(obj.data, "materials"):
                if len(obj.data.materials) == 0:
                    obj.data.materials.append(mat)
                else:
                    obj.data.materials[0] = mat
