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
- 法規チェック・寸法精度保証
- MCPサーバー化（Phase 2 予定）
- LLM API連携（Phase 2 予定）
- GUI自動クリック・インタラクティブ操作

---

## 必要なソフトウェア

| ソフトウェア | バージョン | 入手先 |
|------------|-----------|--------|
| Blender | 4.0 以上 | https://www.blender.org/download/ |
| Python | 3.10 以上 | https://www.python.org/downloads/ |

---

## セットアップ

```bash
# 1. リポジトリクローン
git clone https://github.com/tsailink0611/designfarm-blender-ai-poc.git
cd designfarm-blender-ai-poc

# 2. 依存パッケージインストール
pip install -r requirements.txt

# 3. Blenderのパスを環境変数に設定（Windows）
set BLENDER_PATH=C:\Program Files\Blender Foundation\Blender 4.2\blender.exe

# 4. PYTHONPATHを設定
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
# デフォルトサンプルを実行
.\run_local.ps1

# 日本語指示で実行
.\run_local.ps1 generate "6m×8mの展示ブース。カウンター1つ。パネル3面。モニター2台。"
```

### Windows バッチファイル経由

```bat
cd scripts

REM デフォルトサンプルを実行
run_local.bat

REM 日本語指示で実行
run_local.bat generate "6m×8mの展示ブース"
```

**出力先:**
- `output/cam_top.png` — 俯瞰プレビュー
- `output/cam_visitor.png` — 来場者目線プレビュー

---

## ディレクトリ構成

```
designfarm-blender-ai-poc/
├── README.md
├── requirements.txt
├── docs/
│   ├── architecture.md     # 設計・フロー説明
│   └── roadmap.md          # Phase 1/2/3 ロードマップ
├── samples/
│   ├── prompt_ja_examples.md   # 日本語プロンプトサンプル
│   └── sample_layout_spec.json # JSONサンプル
├── src/
│   ├── app.py              # エントリーポイント（ルートA/B制御）
│   ├── parser/
│   │   ├── instruction_parser.py  # 日本語→JSONパーサー
│   │   └── schema.py              # LayoutSpec Pydanticモデル
│   ├── blender/
│   │   ├── generate_scene.py  # シーン生成メイン（Blender内で実行）
│   │   ├── primitives.py      # 床・壁・什器プリミティブ
│   │   ├── materials.py       # マテリアル定義
│   │   └── camera_setup.py    # カメラ配置・レンダリング
│   └── utils/
│       ├── paths.py        # パス解決
│       └── logger.py       # ロガー設定
├── output/                 # PNG出力先（gitignore対象）
├── scripts/
│   ├── run_local.bat       # Windows バッチ
│   ├── run_local.ps1       # PowerShell
│   └── generate_from_json.py  # JSONラッパー
└── tests/
    ├── test_parser.py      # パーサー単体テスト
    └── test_schema.py      # スキーマ検証テスト
```

---

## テスト実行

```bash
# PYTHONPATHをプロジェクトルートに設定してから実行
set PYTHONPATH=%CD%
python -m pytest tests/ -v
```

---

## 前提・制約

- **Blenderのパス**: `BLENDER_PATH` 環境変数で指定してください。未設定の場合は `C:\Program Files\Blender Foundation\Blender 4.2\blender.exe` を自動検索します
- **PYTHONPATH**: プロジェクトルートに設定する必要があります（`src/` 配下のimportのため）
- **bpyモジュール**: Blender内部でのみ動作します。`src/blender/` 配下のファイルを直接 `python` で実行してもエラーになります（Blenderの `--background --python` 経由で実行してください）
- **動作確認OS**: Windows 11。Mac/Linux は `run_local.ps1` のパスを調整してください
- **レンダリング時間**: CYCLESエンジンでsampels=64の場合、PCスペックにより1枚あたり1〜5分程度かかります。高速確認には `engine: "BLENDER_EEVEE"` への変更も可能です

---

## LLM差し替えについて

`src/parser/instruction_parser.py` の `InstructionParser.parse()` をオーバーライドすることで、テンプレートベースのパーサーをLLM（Claude API / OpenAI API）に差し替えられます。

```python
class ClaudeInstructionParser(InstructionParser):
    def parse(self, instruction: str) -> LayoutSpec:
        # Claude APIを呼び出してJSONを生成
        response = anthropic_client.messages.create(...)
        return LayoutSpec(**json.loads(response.content[0].text))
```

---

## 今後のMCP化方針（Phase 2）

本PoCをMCPサーバー化することで、Claude/ChatGPTからツール呼び出しが可能になります。

```
Claude Desktop
  └─ MCP Server (Python/Node.js)
       └─ generate_layout(instruction: str) → image_url: str
            └─ Blender --background → PNG → Cloudflare R2 → CDN URL
```

参考: [blender-mcp](https://github.com/ahujasid/blender-mcp) — Blender MCP実装の先行事例
