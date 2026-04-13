# Roadmap

## Phase 1: PoC完成（現在）

**目標:** ローカル環境で日本語指示 → PNG出力が動くことを確認する

### 完了
- [x] JSON仕様スキーマ設計（LayoutSpec + Pydantic）
- [x] 日本語テンプレートパーサー（regex + キーワードマッチング）
- [x] Blenderシーン自動生成（床・壁・カウンター・パネル・モニター）
- [x] カメラ2視点レンダリング（俯瞰・来場者目線）
- [x] Windows実行スクリプト（.bat / .ps1）
- [x] サンプルデータ・プロンプト集

### 残タスク
- [ ] 実案件でのプレビュー生成テスト（不動産・建築現場での使用感確認）
- [ ] レンダリング品質の調整（サンプル数・解像度チューニング）
- [ ] エラーメッセージの日本語化

---

## Phase 2: MCPサーバー化

**目標:** Claude Desktop / ChatGPT等からツール呼び出しできるMCPサーバーとして公開する

### 実装内容
- [ ] MCP Server実装（Python / FastMCP）
  - `generate_layout(instruction: str) → image_url: str` ツール定義
  - JSON入力バリデーション → Blender実行 → 画像アップロード → URL返却
- [ ] Cloudflare Workers / R2 連携
  - 生成PNG → R2バケットへアップロード
  - CDN経由のパブリックURL返却
- [ ] LLM APIへのパーサー差し替え
  - Claude API (claude-sonnet) でより精度の高いJSON変換
  - OpenAI API対応（差し替え可能なインターフェース設計済み）
- [ ] 入力バリデーション・エラーハンドリング強化
- [ ] Blender実行のタイムアウト制御

### 参考実装
- [blender-mcp](https://github.com/ahujasid/blender-mcp) — Blender MCP先行事例

### アーキテクチャ（予定）

```
Claude Desktop
  └─ MCP Client
       └─ HTTP → MCP Server (Cloudflare Workers / Python)
                    └─ generate_layout(instruction)
                         ├─ Claude API: 指示文 → JSON
                         ├─ Blender: JSON → PNG
                         └─ R2 Upload → CDN URL返却
```

---

## Phase 3: 協力会社向け提案資料生成・案件提案連携

**目標:** 営業プロセスに組み込み、提案フロー全体を自動化する

### 実装内容
- [ ] 提案PDF自動生成
  - PNG + スペック表 + コメントをPDF化
  - 顧客名・案件名・作成日の自動入力
- [ ] LINE / Slack 連携
  - 生成されたPNG・PDFを営業担当へ自動送信
  - 顧客へのプレビュー共有リンク生成
- [ ] 内装テンプレートライブラリ化
  - 業種別テンプレート（展示会 / ショールーム / 店舗内装）
  - テンプレートから微調整するワークフロー
- [ ] 見積もり連携
  - レイアウトJSONから資材数量・概算見積もりへの変換
  - 見積書PDFの自動生成
- [ ] n8n ワークフロー統合
  - 問い合わせ受信 → 自動プレビュー生成 → 営業担当へ通知
  - NFCタグスキャン → 案件登録 → Blenderプレビュー生成のフロー
