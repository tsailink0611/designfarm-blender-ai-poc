"""
JSONファイルを直接Blenderに渡すシンプルなラッパースクリプト
使用方法: python scripts/generate_from_json.py samples/sample_layout_spec.json
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import route_b

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python scripts/generate_from_json.py <json_path>")
        sys.exit(1)
    route_b(sys.argv[1], Path(__file__).parent.parent)
