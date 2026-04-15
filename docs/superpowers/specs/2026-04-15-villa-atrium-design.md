# Villa Atrium — デザイナーズレジデンス設計仕様

**作成日**: 2026-04-15  
**プロジェクト**: designfarm-blender-ai-poc  
**シーン名**: villa_atrium (シーン5)  
**コンセプト**: ウォームホワイト × 吹き抜けコア型デザイナーズレジデンス

---

## 空間構成

### 全体寸法
- 建物フットプリント: 幅16m (X=-8~+8) × 奥行き14m (Y=-7~+7)
- 1F天井高: 4.0m
- 吹き抜け最高部: 8.0m
- 外観カメラ位置: Y=-20 (ガラスファサード越しに見る)

### ゾーニング
```
[ガラスファサード Y=-7 全幅16m]

1F:
  リビング   : X=-8~0,  Y=-7~+1  (8m×8m)
  ダイニング : X= 0~+8, Y=-7~+1  (8m×8m)
  吹き抜けコア: X=-3~+3, Y=+1~+7  (6m×6m) ← 天井なし・H=8m
  階段室     : X=+3~+8, Y=+1~+7  (5m×6m)

2F:
  左ウィング  : X=-8~-3, Y=-7~+7  (5m×14m) ← 2F床Z=4
  右ウィング  : X=+3~+8, Y=-7~+7  (5m×14m) ← 2F床Z=4
  前ブリッジ  : X=-3~+3, Y=-7~-1  (6m×6m)  ← 2F床Z=4
  後ブリッジ  : X=-3~+3, Y=+5~+7  (6m×2m)  ← 2F床Z=4
  ブリッジ廊下(吹き抜け上): ガラス手すり付き
```

---

## マテリアル設計

| 部位 | マテリアル名 | 仕様 |
|---|---|---|
| 1F床 | `m_marble` | white marble, roughness=0.05, metallic=0.0 |
| 2F床 | `m_walnut` | dark_wooden_planks テクスチャ |
| 壁全般 | `m_concrete` | white concrete, roughness=0.7 |
| ガラスファサード | `m_glass_facade` | transmission=1.0, roughness=0.0, IOR=1.52 |
| 階段段板 | `m_walnut` | ウォールナット木材 |
| 手すりガラス | `m_glass_rail` | transmission=0.9, tint=(0.9,0.95,1.0) |
| スクリーン | `m_screen` | emission, color=(0.3,0.4,0.8), strength=3.0 |
| ブリッジ手すり下端 | `m_bridge_emit` | emission, warm white, strength=2.0 |

---

## 照明設計（7系統）

| ID | 名称 | 種別 | 位置 | 色温度 | 強度 |
|---|---|---|---|---|---|
| L1 | リネアシャンデリア | Chandelier_03モデル + Point | 吹き抜け中央 Z=7m | 2700K warm | 2000W |
| L2 | ガラスファサード外光 | Area Light | Y=-10, facing+Y | 5500K daylight | 3000W |
| L3 | 天井コーニス間接照明 | Emission Strip mesh | 天井際全周 | 3000K warm | emit=2.0 |
| L4 | ブリッジ手すりライン | Emission mesh | 2F手すり下端 | 3200K | emit=1.5 |
| L5 | ダイニングペンダント | hanging_industrial_lamp ×3 | テーブル上 Z=3m | 2700K | 300W×3 |
| L6 | スクリーン発光 | Emission plane | リビング壁面 | 6500K blue | emit=3.0 |
| L7 | 植栽アップライト | Point | 各植物下 | 4000K | 80W×5 |

---

## 家具・造作物リスト

### 1Fリビング (X=-8~0, Y=-7~+1)
- ソファ (Sofa_01): X=-4, Y=-4
- モダンアームチェア ×2: X=-6, Y=-2
- コーヒーテーブル (CoffeeTable_01): X=-4, Y=-3
- スクリーンウォール (4m×2.5m emission plane): X=-7.9, Y=-3, Z=1.5
- 観葉植物 ×3: 各コーナー
- ラグ (fabric texture): ソファ前
- サイドコンソール: X=-7.5, Y=0

### 1Fダイニング (X=0~+8, Y=-7~+1)
- ダイニングテーブル (WoodenTable_01 スケール調整): X=4, Y=-3
- 椅子 ×6: テーブル周囲
- キッチンカウンター (造作): X=7, Y=-2~+1
- ペンダントランプ ×3 (hanging_industrial_lamp): テーブル上

### 吹き抜けコア (X=-3~+3, Y=+1~+7)
- シャンデリア (Chandelier_03): X=0, Y=4, Z=7
- 床: 大理石継続
- 観葉植物 ×2: 吹き抜け床コーナー

### 2F左ウィング → 寝室A
- ベッド (GothicBed_01): X=-6, Y=3
- ナイトスタンド ×2
- 間接照明

### 2F右ウィング → 寝室B / ライブラリ
- デスク + チェア
- シェルフ (Shelf_01)

---

## レンダーアングル4本

| ファイル名 | カメラ位置 | 向き | レンズ | DoF |
|---|---|---|---|---|
| `villa_exterior.png` | (-2, -20, 5) | → (+0, 0, 3) | 50mm | f/8 なし |
| `villa_atrium.png` | (0, 2, 0.5) | 見上げ → (0, 3, 6) | 18mm | f/2.8 |
| `villa_living.png` | (-7.5, -6, 1.5) | → (-2, -1, 1.8) | 24mm | f/3.5 |
| `villa_stair.png` | (5, -3, 1.5) | → (0, 3, 4) | 24mm | f/4 |

---

## 技術仕様

- レンダーエンジン: EEVEE NEXT
- サンプル数: 256
- Bloom: intensity=0.4, radius=5.0
- GTAO: 有効
- SSR: 有効 (大理石床反射)
- カラーグレーディング: Filmic / Medium High Contrast
- 解像度: 1920×1080
- 出力先: `C:/dev/designfarm-blender-ai-poc/output/`

---

## 更新履歴
- 2026-04-15: 初版作成
