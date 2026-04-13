# アーキテクチャ設計

## システム概要

```
[日本語指示文]
      │
      ▼
┌─────────────────────────────────┐
│  InstructionParser              │
│  src/parser/instruction_parser  │
│                                 │
│  regex + キーワードマッチング    │
│  → 寸法・什器数・スタイル抽出   │
│  → LLMに将来差し替え可能        │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  LayoutSpec (JSON)              │
│  src/parser/schema.py           │
│                                 │
│  Pydanticモデルで型検証         │
│  width / depth / height         │
│  walls[] / counters[]           │
│  panels[] / monitors[]          │
│  cameras[] / render{}           │
└──────────────┬──────────────────┘
               │ JSON保存
               ▼
┌─────────────────────────────────┐
│  Blender (バックグラウンド実行)  │
│  src/blender/generate_scene.py  │
│                                 │
│  clear_scene()                  │
│  add_floor / add_wall           │
│  add_counter / add_panel        │
│  add_monitor / add_light        │
│  apply_materials_to_scene()     │
│  setup_cameras()                │
└──────────────┬──────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
┌──────────┐    ┌──────────────┐
│cam_top   │    │cam_visitor   │
│俯瞰視点  │    │来場者目線    │
│PNG出力   │    │PNG出力       │
└──────────┘    └──────────────┘
```

## モジュール責務

| モジュール | 責務 |
|-----------|------|
| `src/parser/schema.py` | LayoutSpec の型定義・バリデーション |
| `src/parser/instruction_parser.py` | 日本語テキスト → LayoutSpec 変換 |
| `src/blender/generate_scene.py` | シーン生成オーケストレーター（Blender内実行） |
| `src/blender/primitives.py` | bpy を使った個別オブジェクト生成 |
| `src/blender/materials.py` | スタイル別マテリアル定義・適用 |
| `src/blender/camera_setup.py` | カメラ配置・レンダリング実行 |
| `src/utils/paths.py` | パス解決・OS差分吸収 |
| `src/utils/logger.py` | ロガー設定 |
| `src/app.py` | ルートA/B のエントリーポイント |

## 実行フロー

### ルートA: 日本語指示 → PNG

```
python src/app.py generate "指示文" --output ./output
  │
  ├─ InstructionParser.parse(instruction)
  │    └─ LayoutSpec オブジェクト生成
  │
  ├─ JSON保存 → output/layout_spec.json
  │
  └─ subprocess: blender --background --python generate_scene.py -- layout.json
       │
       ├─ clear_scene()
       ├─ add_floor(), add_wall() × 4
       ├─ add_counter() × N
       ├─ add_panel() × N
       ├─ add_monitor() × N
       ├─ _add_ambient_light()
       ├─ apply_materials_to_scene()
       └─ setup_cameras() + render_from_camera() × 2
            └─ output/cam_top.png
            └─ output/cam_visitor.png
```

### ルートB: 既存JSON → PNG

```
python src/app.py from-json samples/sample_layout_spec.json
  │
  └─ subprocess: blender --background --python generate_scene.py -- sample.json
       └─ (ルートAのBlender処理と同じ)
```

## 設計判断

### パーサーとBlenderを疎結合にした理由
- パーサー単体のユニットテストが可能（bpyなしでテストできる）
- LLMへの差し替えがBlender側に影響しない
- JSONをファイル経由で渡すことでプロセス分離を実現

### subprocessでBlenderを呼ぶ理由
- bpyはBlender内部のみで動作するため、外部Pythonからimportできない
- `--background` モードでGUIなし実行が可能
- 将来的にMCPサーバーから呼び出す際もこの構造を維持できる

### Pydanticを使った理由
- JSONの型検証・デフォルト値設定を宣言的に記述できる
- `model_dump_json()` でそのままJSONシリアライズ可能
- LLMが出力したJSONのバリデーションにも活用できる
