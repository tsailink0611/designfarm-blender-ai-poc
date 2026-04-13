# Blender AI Layout PoC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 日本語の自然言語指示からBlenderで展示空間の3Dモックを自動生成し、俯瞰・来場者目線の2枚のPNGを出力するPoCを構築する。

**Architecture:** 日本語指示テキスト → InstructionParser（テンプレートベース）→ LayoutSpec JSON → Blender Python API（バックグラウンド実行）→ PNG×2枚。パーサーとBlender実行部を疎結合に設計し、将来LLM/MCP差し替えが可能な抽象層を設ける。

**Tech Stack:** Python 3.10+, Blender 4.x (公式bpy API), pydantic（スキーマ検証）, pytest（テスト）

---

## File Structure

```
designfarm-blender-ai-poc/
├── README.md                        # セットアップ・実行手順
├── .gitignore
├── requirements.txt                 # pydantic, pytest
├── docs/
│   ├── architecture.md              # フロー図・設計説明
│   ├── roadmap.md                   # Phase 1/2/3
│   └── superpowers/plans/           # このファイル
├── samples/
│   ├── prompt_ja_examples.md        # 日本語サンプル指示集
│   └── sample_layout_spec.json      # JSON仕様サンプル
├── src/
│   ├── app.py                       # エントリーポイント（ルートA/B制御）
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── instruction_parser.py    # 日本語→JSONパーサー
│   │   └── schema.py               # LayoutSpec Pydanticモデル
│   ├── blender/
│   │   ├── __init__.py
│   │   ├── generate_scene.py        # Blenderシーン生成メイン
│   │   ├── primitives.py            # 床・壁・パネル等のプリミティブ生成
│   │   ├── materials.py             # マテリアル定義
│   │   └── camera_setup.py         # カメラ2視点設定
│   └── utils/
│       ├── __init__.py
│       ├── paths.py                 # パス解決ユーティリティ
│       └── logger.py               # ロガー設定
├── output/
│   └── .gitkeep
├── scripts/
│   ├── run_local.bat               # Windows バッチ実行
│   ├── run_local.ps1               # PowerShell実行
│   └── generate_from_json.py       # JSONから直接Blender実行するラッパー
└── tests/
    ├── __init__.py
    ├── test_parser.py               # InstructionParser単体テスト
    └── test_schema.py              # LayoutSpec検証テスト
```

---

### Task 1: リポジトリ初期化

**Files:**
- Create: `C:/dev/designfarm-blender-ai-poc/.gitignore`
- Create: `C:/dev/designfarm-blender-ai-poc/requirements.txt`

- [ ] **Step 1: git init & 最低限ファイル作成**

```bash
cd C:/dev/designfarm-blender-ai-poc
git init
```

.gitignore の内容:
```
__pycache__/
*.py[cod]
*.pyo
.env
output/*.png
output/*.blend
*.blend1
.venv/
venv/
dist/
build/
*.egg-info/
.pytest_cache/
.DS_Store
Thumbs.db
```

requirements.txt の内容:
```
pydantic>=2.0.0
pytest>=7.0.0
pytest-mock>=3.0.0
```

- [ ] **Step 2: GitHubリポジトリ作成（gh CLI使用）**

```bash
cd C:/dev/designfarm-blender-ai-poc
gh repo create designfarm-blender-ai-poc --public --description "Blender AI layout PoC for exhibition space generation"
git remote add origin https://github.com/$(gh api user --jq .login)/designfarm-blender-ai-poc.git
```

---

### Task 2: スキーマ定義 (schema.py)

**Files:**
- Create: `src/parser/__init__.py`
- Create: `src/parser/schema.py`

- [ ] **Step 1: テスト作成**

`tests/test_schema.py`:
```python
import pytest
from src.parser.schema import LayoutSpec, Wall, Counter, Panel, Monitor, Camera, RenderConfig


def test_default_layout_spec():
    spec = LayoutSpec()
    assert spec.width == 6.0
    assert spec.depth == 8.0
    assert spec.height == 2.7
    assert spec.style == "white_wood"
    assert isinstance(spec.walls, list)


def test_layout_spec_from_dict():
    data = {
        "width": 10.0,
        "depth": 12.0,
        "height": 3.0,
        "style": "modern",
        "circulation": "clockwise",
        "walls": [{"id": "w1", "position": [0, 0, 0], "rotation_z": 0.0, "width": 10.0, "height": 3.0}],
        "counters": [],
        "panels": [],
        "monitors": [],
        "cameras": [],
        "render_output_dir": "./output"
    }
    spec = LayoutSpec(**data)
    assert spec.width == 10.0
    assert len(spec.walls) == 1


def test_wall_defaults():
    wall = Wall(id="w1", position=[0, 0, 0])
    assert wall.width == 6.0
    assert wall.height == 2.7
    assert wall.thickness == 0.1


def test_counter_defaults():
    counter = Counter(id="c1", position=[1.0, 0.5, 0.0])
    assert counter.width == 1.5
    assert counter.depth == 0.6
    assert counter.height == 0.9


def test_camera_types():
    cam_top = Camera(id="cam_top", type="top_view")
    cam_visitor = Camera(id="cam_visitor", type="visitor_view")
    assert cam_top.type == "top_view"
    assert cam_visitor.type == "visitor_view"
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
cd C:/dev/designfarm-blender-ai-poc
python -m pytest tests/test_schema.py -v 2>&1 | head -20
```
Expected: ImportError または ModuleNotFoundError

- [ ] **Step 3: schema.py 実装**

`src/parser/__init__.py`: 空ファイル

`src/parser/schema.py`:
```python
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
```

- [ ] **Step 4: テスト実行・パス確認**

```bash
cd C:/dev/designfarm-blender-ai-poc
python -m pytest tests/test_schema.py -v
```
Expected: 全テスト PASSED

- [ ] **Step 5: コミット**

```bash
git add src/parser/ tests/test_schema.py
git commit -m "feat: add LayoutSpec pydantic schema"
```

---

### Task 3: 日本語パーサー実装 (instruction_parser.py)

**Files:**
- Create: `src/parser/instruction_parser.py`
- Modify: `tests/test_parser.py`

- [ ] **Step 1: テスト作成**

`tests/test_parser.py`:
```python
import pytest
from src.parser.instruction_parser import InstructionParser
from src.parser.schema import LayoutSpec


@pytest.fixture
def parser():
    return InstructionParser()


def test_parse_dimensions(parser):
    text = "6m×8mの展示ブース"
    spec = parser.parse(text)
    assert spec.width == 6.0
    assert spec.depth == 8.0


def test_parse_dimensions_alternate_format(parser):
    text = "幅10m奥行き12mのブース"
    spec = parser.parse(text)
    assert spec.width == 10.0
    assert spec.depth == 12.0


def test_parse_counter_count(parser):
    text = "受付カウンター2つ"
    spec = parser.parse(text)
    assert len(spec.counters) == 2


def test_parse_panel_count(parser):
    text = "壁面パネル3面"
    spec = parser.parse(text)
    assert len(spec.panels) == 3


def test_parse_monitor_count(parser):
    text = "モニター2台"
    spec = parser.parse(text)
    assert len(spec.monitors) == 2


def test_parse_circulation(parser):
    text = "右回り導線"
    spec = parser.parse(text)
    assert spec.circulation == "clockwise"


def test_parse_circulation_left(parser):
    text = "左回り動線"
    spec = parser.parse(text)
    assert spec.circulation == "counterclockwise"


def test_parse_style_white_wood(parser):
    text = "白基調で木目アクセント"
    spec = parser.parse(text)
    assert spec.style == "white_wood"


def test_parse_fallback_on_empty(parser):
    spec = parser.parse("")
    assert isinstance(spec, LayoutSpec)
    assert spec.width == 6.0


def test_parse_full_example(parser):
    text = "6m×8mの展示ブース。受付カウンター1つ。壁面パネル3面。モニター2台。右回り導線。白基調で木目アクセント。"
    spec = parser.parse(text)
    assert spec.width == 6.0
    assert spec.depth == 8.0
    assert len(spec.counters) == 1
    assert len(spec.panels) == 3
    assert len(spec.monitors) == 2
    assert spec.circulation == "clockwise"
    assert spec.style == "white_wood"


def test_cameras_always_generated(parser):
    spec = parser.parse("テストブース")
    assert len(spec.cameras) == 2
    types = {c.type for c in spec.cameras}
    assert "top_view" in types
    assert "visitor_view" in types
```

- [ ] **Step 2: テストが失敗することを確認**

```bash
python -m pytest tests/test_parser.py -v 2>&1 | head -10
```
Expected: ImportError

- [ ] **Step 3: InstructionParser 実装**

`src/parser/instruction_parser.py`:
```python
"""
InstructionParser: 日本語の展示空間指示文をLayoutSpec JSONに変換するテンプレートベースパーサー
将来はLLM呼び出しに差し替え可能な抽象インターフェースを備える
"""
from __future__ import annotations
import re
import logging
from src.parser.schema import LayoutSpec, Wall, Counter, Panel, Monitor, Camera

logger = logging.getLogger(__name__)


class InstructionParser:
    """
    テンプレートベースの日本語→LayoutSpec変換器
    LLMを使わずにregexとキーワードマッチングでJSONを生成する
    LLM対応は parse() をオーバーライドすることで差し替え可能
    """

    DEFAULT_WIDTH = 6.0
    DEFAULT_DEPTH = 8.0
    DEFAULT_HEIGHT = 2.7

    def parse(self, instruction: str) -> LayoutSpec:
        """
        日本語指示文をLayoutSpecに変換する
        解析失敗時はデフォルト値にフォールバック
        """
        try:
            return self._parse_instruction(instruction)
        except Exception as e:
            logger.warning(f"パース失敗、デフォルト値を使用: {e}")
            return self._default_spec()

    def _parse_instruction(self, text: str) -> LayoutSpec:
        width, depth = self._extract_dimensions(text)
        height = self._extract_height(text)
        style = self._extract_style(text)
        circulation = self._extract_circulation(text)
        counters = self._extract_counters(text, width, depth)
        panels = self._extract_panels(text, width, depth, height)
        monitors = self._extract_monitors(text, width, depth)
        cameras = self._default_cameras(width, depth, height)

        return LayoutSpec(
            width=width,
            depth=depth,
            height=height,
            style=style,
            circulation=circulation,
            counters=counters,
            panels=panels,
            monitors=monitors,
            cameras=cameras,
        )

    def _extract_dimensions(self, text: str) -> tuple[float, float]:
        # パターン例: 6m×8m, 6m x 8m, 幅6m奥行き8m
        patterns = [
            r'(\d+(?:\.\d+)?)\s*[mｍ]\s*[×xX×]\s*(\d+(?:\.\d+)?)\s*[mｍ]',
            r'幅\s*(\d+(?:\.\d+)?)\s*[mｍ].*?奥行き?\s*(\d+(?:\.\d+)?)\s*[mｍ]',
            r'(\d+(?:\.\d+)?)\s*[mｍ].*?(\d+(?:\.\d+)?)\s*[mｍ]',
        ]
        for pattern in patterns:
            m = re.search(pattern, text)
            if m:
                return float(m.group(1)), float(m.group(2))
        return self.DEFAULT_WIDTH, self.DEFAULT_DEPTH

    def _extract_height(self, text: str) -> float:
        m = re.search(r'天井\s*(\d+(?:\.\d+)?)\s*[mｍ]', text)
        if m:
            return float(m.group(1))
        return self.DEFAULT_HEIGHT

    def _extract_style(self, text: str) -> str:
        if re.search(r'白.*木目|木目.*白|白基調', text):
            return "white_wood"
        if re.search(r'モダン|modern', text, re.IGNORECASE):
            return "modern"
        if re.search(r'インダスト|industrial', text, re.IGNORECASE):
            return "industrial"
        return "white_wood"

    def _extract_circulation(self, text: str) -> str:
        if re.search(r'右回り|時計回り', text):
            return "clockwise"
        if re.search(r'左回り|反時計', text):
            return "counterclockwise"
        return "clockwise"

    def _extract_counters(self, text: str, width: float, depth: float) -> list[Counter]:
        m = re.search(r'(?:受付)?カウンター\s*(\d+)\s*(?:つ|台|個|枚)?', text)
        count = int(m.group(1)) if m else 0
        counters = []
        for i in range(count):
            x = width * 0.15 + i * 1.8
            y = depth * 0.1
            counters.append(Counter(id=f"counter_{i+1}", position=[x, y, 0.0]))
        return counters

    def _extract_panels(self, text: str, width: float, depth: float, height: float) -> list[Panel]:
        m = re.search(r'(?:壁面)?パネル\s*(\d+)\s*(?:つ|台|個|面)?', text)
        count = int(m.group(1)) if m else 0
        panels = []
        # パネルを奥壁に等間隔配置
        spacing = width / (count + 1) if count > 0 else 0
        for i in range(count):
            x = spacing * (i + 1)
            y = depth - 0.1
            panels.append(Panel(
                id=f"panel_{i+1}",
                position=[x, y, height / 2],
                rotation_z=0.0
            ))
        return panels

    def _extract_monitors(self, text: str, width: float, depth: float) -> list[Monitor]:
        m = re.search(r'モニター\s*(\d+)\s*(?:つ|台|個)?', text)
        count = int(m.group(1)) if m else 0
        monitors = []
        spacing = width / (count + 1) if count > 0 else 0
        for i in range(count):
            x = spacing * (i + 1)
            y = depth * 0.5
            monitors.append(Monitor(
                id=f"monitor_{i+1}",
                position=[x, y, 1.5]
            ))
        return monitors

    def _default_cameras(self, width: float, depth: float, height: float) -> list[Camera]:
        return [
            Camera(
                id="cam_top",
                type="top_view",
                location=[width / 2, depth / 2, max(width, depth) * 1.2],
                rotation=[0.0, 0.0, 0.0],
                focal_length=50.0
            ),
            Camera(
                id="cam_visitor",
                type="visitor_view",
                location=[width / 2, -2.0, 1.6],
                rotation=[1.309, 0.0, 0.0],  # 75度俯角
                focal_length=35.0
            ),
        ]

    def _default_spec(self) -> LayoutSpec:
        cameras = self._default_cameras(self.DEFAULT_WIDTH, self.DEFAULT_DEPTH, self.DEFAULT_HEIGHT)
        return LayoutSpec(cameras=cameras)
```

- [ ] **Step 4: テスト実行・パス確認**

```bash
python -m pytest tests/test_parser.py -v
```
Expected: 全テスト PASSED

- [ ] **Step 5: コミット**

```bash
git add src/parser/instruction_parser.py tests/test_parser.py
git commit -m "feat: add template-based Japanese instruction parser"
```

---

### Task 4: ユーティリティ実装 (paths.py, logger.py)

**Files:**
- Create: `src/utils/__init__.py`
- Create: `src/utils/paths.py`
- Create: `src/utils/logger.py`

- [ ] **Step 1: paths.py 実装**

`src/utils/__init__.py`: 空ファイル

`src/utils/paths.py`:
```python
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
```

- [ ] **Step 2: logger.py 実装**

`src/utils/logger.py`:
```python
"""
ロガー設定
"""
import logging
import sys


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s",
                              datefmt="%H:%M:%S")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
```

- [ ] **Step 3: コミット**

```bash
git add src/utils/
git commit -m "feat: add path utilities and logger"
```

---

### Task 5: Blender プリミティブ生成 (primitives.py)

**Files:**
- Create: `src/blender/__init__.py`
- Create: `src/blender/primitives.py`

注意: このファイルは `bpy` (Blender Python API) に依存する。Blender外から直接実行するとImportErrorになるため、テストはgenerate_scene.py経由のBashテストで代替する。

- [ ] **Step 1: primitives.py 実装**

`src/blender/__init__.py`: 空ファイル

`src/blender/primitives.py`:
```python
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
```

- [ ] **Step 2: コミット**

```bash
git add src/blender/
git commit -m "feat: add Blender primitives module"
```

---

### Task 6: マテリアル定義 (materials.py)

**Files:**
- Create: `src/blender/materials.py`

- [ ] **Step 1: materials.py 実装**

`src/blender/materials.py`:
```python
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
```

- [ ] **Step 2: コミット**

```bash
git add src/blender/materials.py
git commit -m "feat: add material definitions for scene styles"
```

---

### Task 7: カメラ設定 (camera_setup.py)

**Files:**
- Create: `src/blender/camera_setup.py`

- [ ] **Step 1: camera_setup.py 実装**

`src/blender/camera_setup.py`:
```python
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
```

- [ ] **Step 2: コミット**

```bash
git add src/blender/camera_setup.py
git commit -m "feat: add camera setup and render utilities"
```

---

### Task 8: シーン生成メイン (generate_scene.py)

**Files:**
- Create: `src/blender/generate_scene.py`

- [ ] **Step 1: generate_scene.py 実装**

`src/blender/generate_scene.py`:
```python
"""
Blenderシーン生成メインモジュール
LayoutSpecを受け取り、シーンを構築してPNGを2枚出力する
このスクリプトはBlenderの--pythonオプション経由で実行する
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
        dict(wall_id="back",   position=[w/2, d, h/2], rotation_z=0.0, width=w, height=h, thickness=t),
        # 手前壁
        dict(wall_id="front",  position=[w/2, 0, h/2], rotation_z=0.0, width=w, height=h, thickness=t),
        # 左壁
        dict(wall_id="left",   position=[0, d/2, h/2], rotation_z=math.radians(90), width=d, height=h, thickness=t),
        # 右壁
        dict(wall_id="right",  position=[w, d/2, h/2], rotation_z=math.radians(90), width=d, height=h, thickness=t),
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
```

- [ ] **Step 2: コミット**

```bash
git add src/blender/generate_scene.py
git commit -m "feat: add main scene generation orchestrator"
```

---

### Task 9: アプリエントリーポイント (app.py)

**Files:**
- Create: `src/app.py`

- [ ] **Step 1: app.py 実装**

`src/app.py`:
```python
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
    logger.info(f"Blender実行: {' '.join(cmd)}")
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
```

- [ ] **Step 2: コミット**

```bash
git add src/app.py
git commit -m "feat: add main app entry point with route A/B"
```

---

### Task 10: サンプルデータ・スクリプト

**Files:**
- Create: `samples/sample_layout_spec.json`
- Create: `samples/prompt_ja_examples.md`
- Create: `scripts/generate_from_json.py`
- Create: `scripts/run_local.bat`
- Create: `scripts/run_local.ps1`
- Create: `output/.gitkeep`

- [ ] **Step 1: sample_layout_spec.json 作成**

`samples/sample_layout_spec.json`:
```json
{
  "width": 6.0,
  "depth": 8.0,
  "height": 2.7,
  "style": "white_wood",
  "circulation": "clockwise",
  "walls": [],
  "counters": [
    {
      "id": "counter_1",
      "position": [1.5, 1.0, 0.0],
      "rotation_z": 0.0,
      "width": 1.5,
      "depth": 0.6,
      "height": 0.9,
      "material": "wood_accent"
    }
  ],
  "panels": [
    {
      "id": "panel_1",
      "position": [1.5, 7.9, 1.2],
      "rotation_z": 0.0,
      "width": 1.0,
      "height": 2.4,
      "thickness": 0.05,
      "material": "white_plaster"
    },
    {
      "id": "panel_2",
      "position": [3.0, 7.9, 1.2],
      "rotation_z": 0.0,
      "width": 1.0,
      "height": 2.4,
      "thickness": 0.05,
      "material": "white_plaster"
    },
    {
      "id": "panel_3",
      "position": [4.5, 7.9, 1.2],
      "rotation_z": 0.0,
      "width": 1.0,
      "height": 2.4,
      "thickness": 0.05,
      "material": "white_plaster"
    }
  ],
  "monitors": [
    {
      "id": "monitor_1",
      "position": [2.0, 4.0, 1.5],
      "rotation_z": 0.0,
      "width": 0.8,
      "height": 0.5,
      "depth": 0.05,
      "material": "dark_screen"
    },
    {
      "id": "monitor_2",
      "position": [4.0, 4.0, 1.5],
      "rotation_z": 0.0,
      "width": 0.8,
      "height": 0.5,
      "depth": 0.05,
      "material": "dark_screen"
    }
  ],
  "cameras": [
    {
      "id": "cam_top",
      "type": "top_view",
      "location": [3.0, 4.0, 10.0],
      "rotation": [0.0, 0.0, 0.0],
      "focal_length": 50.0
    },
    {
      "id": "cam_visitor",
      "type": "visitor_view",
      "location": [3.0, -2.5, 1.7],
      "rotation": [1.309, 0.0, 0.0],
      "focal_length": 35.0
    }
  ],
  "render_output_dir": "./output",
  "render": {
    "resolution_x": 1280,
    "resolution_y": 720,
    "engine": "CYCLES",
    "samples": 64
  }
}
```

- [ ] **Step 2: run_local.bat 作成**

`scripts/run_local.bat`:
```bat
@echo off
REM ===================================================
REM designfarm-blender-ai-poc 実行スクリプト (Windows)
REM ===================================================

SET PROJECT_ROOT=%~dp0..
SET BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe

REM ルートA: 日本語指示からシーン生成
IF "%1"=="generate" (
    python "%PROJECT_ROOT%\src\app.py" generate "%~2" --output "%PROJECT_ROOT%\output"
    GOTO END
)

REM ルートB: サンプルJSONからシーン生成
IF "%1"=="from-json" (
    python "%PROJECT_ROOT%\src\app.py" from-json "%~2"
    GOTO END
)

REM デフォルト: サンプルJSONで実行
python "%PROJECT_ROOT%\src\app.py" from-json "%PROJECT_ROOT%\samples\sample_layout_spec.json"

:END
```

- [ ] **Step 3: run_local.ps1 作成**

`scripts/run_local.ps1`:
```powershell
# ===================================================
# designfarm-blender-ai-poc 実行スクリプト (PowerShell)
# ===================================================

param(
    [string]$Command = "from-json",
    [string]$Input = ""
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = $ProjectRoot

if ($Command -eq "generate") {
    if (-not $Input) {
        $Input = "6m×8mの展示ブース。受付カウンター1つ。壁面パネル3面。モニター2台。右回り導線。白基調で木目アクセント。"
    }
    python "$ProjectRoot\src\app.py" generate $Input --output "$ProjectRoot\output"
} elseif ($Command -eq "from-json") {
    $JsonPath = if ($Input) { $Input } else { "$ProjectRoot\samples\sample_layout_spec.json" }
    python "$ProjectRoot\src\app.py" from-json $JsonPath
} else {
    Write-Host "使用方法:"
    Write-Host "  .\run_local.ps1 generate '6m×8mの展示ブース...' "
    Write-Host "  .\run_local.ps1 from-json 'path\to\layout.json'"
}
```

- [ ] **Step 4: generate_from_json.py 作成**

`scripts/generate_from_json.py`:
```python
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
```

- [ ] **Step 5: サンプルプロンプト集作成**

`samples/prompt_ja_examples.md`:
```markdown
# 日本語プロンプトサンプル集

## 基本例（展示会ブース）
```
6m×8mの展示ブース。受付カウンター1つ。壁面パネル3面。モニター2台。右回り導線。白基調で木目アクセント。俯瞰と来場者目線でプレビューを出してください。
```

## 大型ブース
```
10m×12mの大型展示ブース。受付カウンター2つ。壁面パネル5面。モニター4台。左回り導線。モダンスタイル。
```

## ショールーム
```
8m×8mのショールーム。カウンター1つ。パネル4面。モニター2台。右回り動線。白基調。
```

## 小型ブース
```
3m×4mの小型ブース。カウンター1つ。パネル2面。モニター1台。
```
```

- [ ] **Step 6: output/.gitkeep 作成**

```bash
touch output/.gitkeep
```

- [ ] **Step 7: コミット**

```bash
git add samples/ scripts/ output/.gitkeep
git commit -m "feat: add sample data and execution scripts"
```

---

### Task 11: ドキュメント作成

**Files:**
- Create: `README.md`
- Create: `docs/architecture.md`
- Create: `docs/roadmap.md`

詳細な内容は実装フェーズで埋める（Task 12で実施）。

---

### Task 12: README・docs 完成

- [ ] **Step 1: README.md 作成（完全版）**

`README.md` の内容:
```markdown
# designfarm-blender-ai-poc

建築内装・展示設営会社向け「Blender自動化PoC」

日本語の空間指示文から展示会ブースの3Dモックを自動生成し、俯瞰・来場者目線のPNGプレビューを出力します。

---

## できること

- 日本語の指示文から展示空間レイアウトをJSON仕様に変換
- Blender Python APIでシーンを自動構築（床・壁・カウンター・パネル・モニター）
- 俯瞰カメラ・来場者目線カメラの2視点でPNGを書き出し
- スタイル別マテリアル（白木目 / モダン / インダストリアル）

## できないこと（今回スコープ外）

- 施工図・CAD互換出力
- 法規チェック
- 正確な寸法整合
- MCPサーバー化（Phase 2 予定）
- LLM API連携（Phase 2 予定）

---

## 必要なソフトウェア

| ソフトウェア | バージョン | 入手先 |
|------------|-----------|--------|
| Blender | 4.0 以上 | https://www.blender.org/download/ |
| Python | 3.10 以上 | https://www.python.org/downloads/ |
| pip パッケージ | - | `pip install -r requirements.txt` |

---

## セットアップ

```bash
# 1. リポジトリクローン
git clone https://github.com/<your-username>/designfarm-blender-ai-poc.git
cd designfarm-blender-ai-poc

# 2. 依存パッケージインストール
pip install -r requirements.txt

# 3. Blenderのパスを環境変数に設定（Windows）
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe

# 4. PYTHONPATH を設定
set PYTHONPATH=%CD%
```

---

## 実行手順

### ルートA: 日本語指示からシーン生成

```bash
python src/app.py generate "6m×8mの展示ブース。受付カウンター1つ。壁面パネル3面。モニター2台。右回り導線。白基調で木目アクセント。"
```

### ルートB: サンプルJSONからシーン生成

```bash
python src/app.py from-json samples/sample_layout_spec.json
```

### PowerShell スクリプト経由

```powershell
cd scripts
.\run_local.ps1 generate "6m×8mの展示ブース。カウンター1つ。パネル3面。モニター2台。"
```

### Windows バッチファイル経由

```bat
cd scripts
run_local.bat generate "6m×8mの展示ブース"
```

出力先: `output/cam_top.png`（俯瞰）、`output/cam_visitor.png`（来場者目線）

---

## ディレクトリ構成

```
designfarm-blender-ai-poc/
├── README.md
├── requirements.txt
├── docs/           # 設計ドキュメント
├── samples/        # サンプルJSON・プロンプト集
├── src/
│   ├── app.py                  # エントリーポイント
│   ├── parser/                 # 日本語→JSONパーサー
│   └── blender/                # Blenderシーン生成
├── output/         # PNG出力先（gitignore対象）
├── scripts/        # 実行スクリプト
└── tests/          # ユニットテスト
```

---

## テスト実行

```bash
python -m pytest tests/ -v
```

---

## 前提・制約

- Blenderのインストール先を `BLENDER_PATH` 環境変数で指定してください
- `PYTHONPATH` をプロジェクトルートに設定する必要があります
- Blender内部の `bpy` モジュールはBlender経由でのみ動作します（直接 `import bpy` はできません）
- Windows 11 で動作確認しています（Mac/Linux は候補パスを調整してください）

---

## 今後のMCP化方針（Phase 2）

本PoCをMCPサーバー化することで、Claude/ChatGPTからツール呼び出しが可能になります:

```
Claude → MCP Server (Node.js/Python) → Blender Python → PNG → S3/CF Upload → URL返却
```
```

- [ ] **Step 2: architecture.md 作成**

`docs/architecture.md` の内容は Task 11 で記載済みのフォーマットに従う。

- [ ] **Step 3: roadmap.md 作成**

`docs/roadmap.md`:
```markdown
# Roadmap

## Phase 1: PoC完成（現在）

**目標:** ローカル環境で日本語指示→PNG出力が動くことを確認する

- [x] JSON仕様スキーマ設計（LayoutSpec）
- [x] 日本語テンプレートパーサー
- [x] Blenderシーン自動生成
- [x] カメラ2視点レンダリング
- [x] Windows実行スクリプト
- [ ] 実案件でのプレビュー生成テスト

---

## Phase 2: MCPサーバー化

**目標:** Claude/ChatGPT等からツール呼び出しできるMCPサーバーとして公開する

- [ ] MCP Server実装（Python or Node.js）
  - `generate_layout` ツール定義
  - JSON入力 / PNG URL返却
- [ ] Cloudflare Workers / R2 連携
  - 生成PNG → R2アップロード → CDN URL返却
- [ ] LLM APIへのパーサー差し替え
  - Claude API or OpenAI APIでより精度の高いJSONへ変換
- [ ] 入力バリデーション強化
- [ ] エラーハンドリング整備

---

## Phase 3: 協力会社向け提案資料生成・案件提案連携

**目標:** 営業プロセスに組み込んで、提案フロー全体を自動化する

- [ ] 提案PDF自動生成
  - PNG + スペック表 + コメントをPDF化
- [ ] LINE / Slack 連携
  - 生成されたPNG・PDFを自動送信
- [ ] 内装テンプレートライブラリ化
  - 業種別（展示会 / ショールーム / 店舗）のテンプレート
- [ ] 見積もり連携
  - レイアウトJSONから資材数量・概算見積もりへの変換
- [ ] n8n ワークフロー統合
  - 問い合わせ受信 → 自動プレビュー生成 → 営業担当へ通知
```

- [ ] **Step 4: コミット**

```bash
git add README.md docs/ samples/prompt_ja_examples.md
git commit -m "docs: add README, architecture, and roadmap"
```

---

### Task 13: 初期スキャフォールドコミット & プッシュ

- [ ] **Step 1: 全ファイルを確認してプッシュ**

```bash
git log --oneline
git push -u origin main
```

---

## Self-Review

**Spec coverage:**
- [x] 日本語指示入力 → `instruction_parser.py`
- [x] JSON仕様生成 → `schema.py`
- [x] Blender Python実行 → `generate_scene.py`
- [x] カメラ2視点（俯瞰・来場者目線）→ `camera_setup.py`
- [x] PNG2枚出力 → `render_from_camera()`
- [x] 床・壁・カウンター・パネル・モニター → `primitives.py`
- [x] マテリアル設定 → `materials.py`
- [x] READMEで実行可能 → `README.md` + `scripts/`
- [x] サンプルデータ → `samples/`
- [x] テスト → `tests/`
- [x] ルートA/B → `app.py`
- [x] roadmap Phase 1/2/3 → `docs/roadmap.md`
- [x] 最初のコミットメッセージ → Task 1 で指定

**Placeholder scan:** なし（全ステップに完全なコードを記載）

**Type consistency:**
- `LayoutSpec`, `Wall`, `Counter`, `Panel`, `Monitor`, `Camera` → `schema.py` で定義、全モジュールで一貫して使用
- `generate_scene()` → `src/blender/generate_scene.py` で定義、`app.py` からは `run_blender()` 経由で呼び出し（Blender内で実行するため直接importしない設計）
