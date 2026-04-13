"""
app.py: メインエントリーポイント
ルートA: 日本語指示 -> JSON生成 -> Blender実行 -> PNG出力
ルートB: 既存JSON読込 -> Blender実行 -> PNG出力
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path

from src.parser.instruction_parser import InstructionParser
from src.parser.schema import LayoutSpec
from src.utils.paths import resolve_output_dir
from src.utils.logger import get_logger

logger = get_logger(__name__)


def find_blender_executable() -> str:
    """
    Blender実行ファイルを探す
    環境変数 BLENDER_PATH があればそれを使用、なければデフォルトパスを試みる
    """
    import os
    if "BLENDER_PATH" in os.environ:
        return os.environ["BLENDER_PATH"]

    candidates = [
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        "/usr/bin/blender",
        "/Applications/Blender.app/Contents/MacOS/Blender",
    ]
    for path in candidates:
        if Path(path).exists():
            return path

    raise FileNotFoundError(
        "Blenderが見つかりません。BLENDER_PATH環境変数を設定してください。\n"
        "例: set BLENDER_PATH=C:\\Program Files\\Blender Foundation\\Blender 4.2\\blender.exe"
    )


def run_blender(json_path: Path, project_root: Path) -> int:
    """Blenderをバックグラウンドで実行してシーンを生成する"""
    blender_exe = find_blender_executable()
    generate_script = project_root / "src" / "blender" / "generate_scene.py"

    cmd = [
        blender_exe,
        "--background",
        "--python", str(generate_script),
        "--",
        str(json_path),
    ]
    logger.info(f"Blender実行: {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def route_a(instruction: str, output_dir: str, project_root: Path) -> None:
    """ルートA: 日本語指示 -> JSON -> Blender実行"""
    logger.info("ルートA: 日本語指示からシーン生成")
    parser = InstructionParser()
    spec = parser.parse(instruction)
    spec.render_output_dir = output_dir

    output_path = resolve_output_dir(output_dir)
    json_path = output_path / "layout_spec.json"
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(spec.model_dump_json(indent=2))
    logger.info(f"JSON保存: {json_path}")

    returncode = run_blender(json_path, project_root)
    if returncode != 0:
        logger.error(f"Blender実行失敗 (returncode={returncode})")
        sys.exit(returncode)


def route_b(json_path: str, project_root: Path) -> None:
    """ルートB: 既存JSONからBlender実行"""
    logger.info(f"ルートB: {json_path} からシーン生成")
    returncode = run_blender(Path(json_path), project_root)
    if returncode != 0:
        logger.error(f"Blender実行失敗 (returncode={returncode})")
        sys.exit(returncode)


def main() -> None:
    parser = argparse.ArgumentParser(description="Blender AI Layout PoC")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ルートA
    gen_parser = subparsers.add_parser("generate", help="日本語指示からシーン生成")
    gen_parser.add_argument("instruction", help="日本語の空間指示文")
    gen_parser.add_argument("--output", default="./output", help="出力ディレクトリ")

    # ルートB
    from_json_parser = subparsers.add_parser("from-json", help="既存JSONからシーン生成")
    from_json_parser.add_argument("json_path", help="layout_spec.jsonのパス")

    args = parser.parse_args()
    project_root = Path(__file__).parent.parent

    if args.command == "generate":
        route_a(args.instruction, args.output, project_root)
    elif args.command == "from-json":
        route_b(args.json_path, project_root)


if __name__ == "__main__":
    main()
