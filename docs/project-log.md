# DesignFarm Blender AI PoC — プロジェクト記録

## プロジェクト概要
- **目的**: 言葉でBlenderの3Dパースを自動生成するPoCシステム
- **技術**: Claude Code + BlenderMCP (port 9876) + Poly Haven + Sketchfab
- **用途**: DesignFarm社デザイナー向けデモ、商業施設競争入札の初稿提案

---

## 作成済みシーン

### シーン1: 展示会ブース (Exhibition Booth)
- **ファイル**: `output/demo_v3_textured.png`, `output/demo_real_people_v2.png`
- **空間**: 8m × 6m × 3.2m
- **特徴**:
  - ネイビーアクセント壁 + ウッドスラット
  - シーリングLEDストリップ (Cool白 + Warm琥珀 + Teal)
  - 受付カウンター + 展示プラットフォーム
  - 3Dプロダクト展示 (赤キューブ・青メタリック球・緑シリンダー)
  - 観葉植物 × 4
  - Sketchfab人物: Dennis (ビジネスマン) + Fabienne & Percy (母子)
- **マテリアル**: Poly Haven `dark_wooden_planks` (床), `beige_wall_001` (壁)

### シーン2: モダンカフェ 50席 (Modern Cafe)
- **ファイル**: `output/cafe_final.png`, `output/cafe_seated_corner.png` (最新・推奨)
- **空間**: 16m × 12m × 3.8m
- **参考**: Google Images検索 (Playwright) — 日本風モダンカフェ, ウォームウッド照明
- **特徴**:
  - ダークウッド + ウォームアンバーペンダントライト (グローブ型 × 26個)
  - 4人テーブル × 12 (48席) + 窓際カウンター × 8席 = 56席
  - バリスタカウンター (奥壁全幅) + バーストール × 8
  - ウッドスラットアクセントパネル (奥壁)
  - 観葉植物 × 5
  - Sketchfab人物: Dennis × 6 + Fabienne&Percy × 5 + Sophia × 6 = 17体
  - 着席フィギュア (幾何学) × 39体 — 全12テーブルに2〜4人ずつ配置
  - 総人数: 立ち17体 + 座り39体 = 56人
- **マテリアル**: Poly Haven `dark_wooden_planks` (床), `beige_wall_001` (壁)
- **着席フィギュア仕様**: 頭/髪/首/肩/胴/腰/大腿/下腿/腕を個別シリンダーで構成、8色の服装バリエーション

---

## 使用アセット
| アセット | ソース | 用途 |
|---|---|---|
| dark_wooden_planks | Poly Haven (1k) | 床テクスチャ |
| beige_wall_001 | Poly Haven (1k) | 壁テクスチャ |
| Dennis Posed 004 | Sketchfab / renderpeople | 男性立ち姿 |
| Fabienne & Percy 001 | Sketchfab / renderpeople | 母子立ち姿 |

---

## Sketchfab API
- アカウント: 設定済み (BlenderMCPパネル)
- キー管理: セッション内のみ使用、ファイルには非記録

---

## 技術メモ
- Cycles レンダリングはMCP接続タイムアウトのため手動 (F12) を推奨
- EEVEE NEXT: `taa_render_samples=256`, Bloom, GTAO, SSR有効
- Filmic + High Contrast カラーグレーディング
- 人物モデルはlinked duplicateでメモリ節約
- `bpy.ops.object.duplicate(linked=True)` で同一メッシュを複数配置

---

### シーン3: LUMIS展示ブース — 架空企業 (Exhibition Booth APEX)
- **ファイル**: `output/lumis_final2.png`
- **空間**: 展示ホール40m×30m×10m、ブース15m×9m×5.5m
- **コンセプト**: 「暗闇から浮かぶ光の要塞」— 漆黒×電気シアン×ディープパープル
- **特徴**:
  - 二重構造アーチ (外:チャコール / 内:シアン発光LED)
  - 前方キャノピー3m張り出し
  - 垂直光柱 × 4本 (床〜天井)
  - ミラーフロア (高光沢SSR反射)
  - 浮遊プロダクト展示台 × 3基
  - メインスクリーン 4m×2.5m + サイドパネル × 4枚
  - Sketchfab人物 × 18体 (Dennis×7, Sophia×7, Fabienne&Percy×4)
  - 天井トラス構造 + スポットライト × 17灯
- **照明**: クール白 × 8 + シアン × 4 + パープル × 2 + ウォーム × 3 + 来場者エリア × 7
- **EEVEE設定**: Bloom(intensity=1.5, radius=7.0) + SSR + GTAO
- **技術メモ**:
  - linked duplicate時は子孫のhide_renderも手動でFalseにする必要あり
  - `for child in obj.children_recursive: child.hide_render = False`

---

### シーン4: NOVA/Zephyr展示ブース — 受賞レベルリデザイン (Nova Pavilion v2)

- **ファイル**:
  - `output/nova_v4_dof.png` 〜 `nova_v7_lounge_close.png` — 第1世代
  - `output/nova_final_hero.png` — 正面ヒーローショット（推奨）
  - `output/nova_diagonal.png` — 45度斜め・奥行き強調
  - `output/nova_entrance.png` — 入口ゲートからの構図（人物フレーム）
- **コンセプト**: 漆黒×ゴールドロゴ×磨きコンクリート × 劇場型照明 × 複雑建築構造
- **Nova Pavilion v2 構造要素（82個のPV_オブジェクト）**:
  - 二重入口ブレード (PV_BladeL/R) + エントリーリンテル
  - 天井ビームグリッド (PV_BeamX × 5本 + PV_BeamY × 5本 = 格子状)
  - LEDパネル × 6基 (天井格子内、発光強度8.0)
  - レリーフ背面壁 (PV_Rel_A〜H = 8枚の奥行きパネル)
  - ZEPHYRロゴウォール (白発光バックパネル + ゴールド発光3Dテキスト)
  - 高台ステージ (PV_Stage + ステップ、高さ0.35m)
  - L字カウンター + マーブルトップ
  - ディスプレイシェルフ × 9基 (右壁)
  - プリンス × 3基 (ステージ上製品展示台)
  - 4本柱 (0.35m角、アンバーアップライト付き)
  - バーチカルフィン × 3 (右壁建築装飾)
- **使用Poly Haven実モデル**:
  - `modern_arm_chair_01` — ラウンジアームチェア（木フレーム＋レザー）
  - `Sofa_01` — ラウンジソファ
  - `CoffeeTable_01` — コーヒーテーブル
  - `bar_chair_round_01` × 4 — カウンターバースツール
  - `modern_ceiling_lamp_01` × 6 — ペンダントランプ（本物モデル）
  - `Shelf_01` × 2 — 製品展示棚
  - `ceramic_vase_01/02` — 花瓶（テーブル・カウンター装飾）
  - `anthurium_botany_01` × 6, `calathea_orbifolia_01` × 5 — 観葉植物
- **マテリアル**:
  - `m_jetblack` (roughness=0.15, metallic=0.1) — 壁・柱・Canopy
  - `m_marble` (roughness=0.05) — カウンタートップ
  - `m_floor_gloss` (roughness=0.05) — 磨きコンクリート床（SSR反射）
  - `m_gold` (metallic=1.0, emission×0.4) — ZEPHYRロゴテキスト（発光ゴールド）
  - `m_logo_wall` (emission=1.2) — ロゴバックパネル（白発光）
  - `m_screen` (emission) — ブルー発光スクリーン
- **照明（24基）**:
  - PL_LED0-5: LEDシーリングパネルポイントライト (1200W × 6)
  - SP_Gate_L/R: ゲートビームスポット (6000W × 2、25°)
  - SP_Logo1/2: ロゴ専用ビーム (8000W + 補助)
  - SP_Cnt_L/R: カウンタービーム (3000W × 2)
  - SP_Plinth0-2: プリンスポットライト (4000W × 3)
  - UP_Col0-3: 柱アンバーアップライト (600W × 4)
  - SP_Plant1/2: 植物グリーンアクセント
  - LA_Lounge: ラウンジエリアライト (400W)
  - SP_Shelf/Fin: 棚・フィン用スポット
- **テキスト**: 3Dテキスト「ZEPHYR」（発光ゴールド, extrude=0.03m）+ 「PREMIUM SPACES」（白）
- **HDRI**: 完全オフ (strength=0.0)、World background= 漆黒
- **レンダー**: EEVEE NEXT 256samples, Filmic High Contrast, DoF有効
- **技術メモ**:
  - PV_Rel_F (中央リリーフパネル) はZEPHYRテキストと重なるため削除
  - transform_apply後はobj.location=(0,0,0)だが頂点は正位置にある
  - linked duplicate後は children_recursive の hide_render も手動でFalseに

---

## 次のステップ候補
- [ ] 着席人物モデルの追加
- [ ] Cyclesレンダリングでフォトリアル出力
- [ ] カメラアニメーション (ウォークスルー動画)
- [ ] 写真入力からのレイアウト自動推定
- [ ] SVG平面図の自動出力

---

## 更新履歴
- 2026-04-14: PoC開始、展示会ブースシーン完成
- 2026-04-14: MCPサーバー接続確立、Poly Havenテクスチャ適用
- 2026-04-14: Sketchfab連携確立、リアル人物モデル追加
- 2026-04-14: モダンカフェ50席シーン作成
- 2026-04-14: 着席フィギュア×39体追加 (全12テーブル配置), cafe_seated_corner.png 完成
- 2026-04-15: LUMIS展示ブース制作開始 (架空企業、競合DesignFarm対抗)
- 2026-04-15: LUMISブース完成 — 18人 + ミラーフロア + シアンLED, lumis_final2.png
- 2026-04-15: Poly Haven実モデル8種ダウンロード（家具・ランプ・棚・花瓶）
- 2026-04-15: NOVAブース全面リデザイン — ジェットブラック × ゴールドロゴ × 磨きコンクリート床 × 劇場型照明10系統
- 2026-04-15: 4アングルレンダリング完成 (nova_v4_dof〜nova_v7_lounge_close)
- 2026-04-15: Nova Pavilion v2 完成 — 82個PV_オブジェクト、複雑建築構造、ゴールドZEPHYRロゴ発光
- 2026-04-15: 3アングル追加レンダリング完成 (nova_final_hero / nova_diagonal / nova_entrance)
