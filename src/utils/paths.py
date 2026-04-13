"""
パス解決ユーティリティ
Windows/Mac/Linux 対応のパス正規化
"""
from __future__ import annotations
from pathlib import Path


def resolve_output_dir(base_dir: str | Path) -> Path:
    """出力ディレクトリを絶対パスに変換し、存在しなければ作成する"""
    path = Path(base_dir).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def blender_safe_path(path: str | Path) -> str:
    """Blender Python APIに渡せる形式（スラッシュ統一）に変換する"""
    return str(Path(path).resolve()).replace("\\", "/")
