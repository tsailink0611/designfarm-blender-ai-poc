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
