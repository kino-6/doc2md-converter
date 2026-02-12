# Document to Markdown Converter (doc2md)

高品質なMarkdown変換を実現する、Word (.docx)、Excel (.xlsx)、PDF (.pdf) ドキュメント変換ツール。

## 特徴

- ✅ **複数フォーマット対応**: Word、Excel、PDFを統一的に処理
- ✅ **高品質変換**: テキスト、表、画像、見出し構造を保持
- ✅ **画像抽出**: 埋め込み画像とベクターグラフィックを自動抽出
- ✅ **進捗表示**: tqdmによる視覚的な進捗バー
- ✅ **エンコーディング対応**: UTF-8で正しく出力
- ✅ **バッチ処理**: 複数ファイルの一括変換
- ✅ **設定ファイル**: YAMLによる柔軟な設定
- ✅ **LLM品質評価**: Ollamaによる変換品質の自動評価（オプション、評価のみで修正機能なし）

## インストール

### 基本インストール

```bash
pip install -e .
```

### 開発環境

```bash
pip install -e ".[dev]"
```

### LLM評価機能を含む

```bash
pip install -e ".[dev,llm]"
```

## 使用方法

### 基本的な使い方

```bash
# 単一ファイルの変換
doc2md -i document.docx -o output.md

# 画像抽出を有効化
doc2md -i document.pdf -o output.md --extract-images

# 複数ファイルの一括変換
doc2md -i file1.docx -i file2.xlsx -i file3.pdf

# 設定ファイルを使用
doc2md -i document.pdf -c config.yaml
```

### 高度な使い方

```bash
# メタデータを含める
doc2md -i document.docx -o output.md --include-metadata

# 見出しレベルをオフセット
doc2md -i document.docx -o output.md --heading-offset 1

# プレビューモード（最初の50行のみ表示）
doc2md -i document.pdf --preview

# ドライランモード（ファイル出力なし）
doc2md -i document.docx --dry-run

# 画像をBase64埋め込み
doc2md -i document.pdf -o output.md --embed-images-base64
```

### 設定ファイルの例

```yaml
# config.yaml
extract_images: true
include_metadata: true
heading_offset: 0
ocr_lang: "eng+jpn"
max_file_size_mb: 100
```

## 機能詳細

### サポートされるフォーマット

| フォーマット | 拡張子 | テキスト | 表 | 画像 | 見出し |
|------------|--------|---------|-----|------|--------|
| Word       | .docx  | ✅      | ✅  | ✅   | ✅     |
| Excel      | .xlsx  | ✅      | ✅  | ❌   | ✅     |
| PDF        | .pdf   | ✅      | ✅  | ✅   | ✅     |

### 画像抽出

- **埋め込み画像**: JPEG、PNG、GIFなどの画像を抽出
- **ベクターグラフィック**: 図表、回路図などを144 DPIでPNG化
- **自動検出**: ページ内の描画オブジェクト数とテキスト比率で判定

### 進捗表示

```
画像抽出中: 100%|█████████████████████████| 13/13 [00:00<00:00, 28.29ページ/s]
PDFページ処理中: 100%|████████████████████| 13/13 [00:01<00:00,  6.69ページ/s]
```

### LLM品質評価（オプション）

**重要な注意**: 
- この機能は**品質評価のみ**を行います（スコアリングと問題点の指摘）
- **文章の自動修正や誤字脱字の修正は行いません**
- 変換プロセスとは独立しており、CLIには統合されていません
- 別途スクリプトとして提供されています

#### 前提条件

1. **Ollamaのインストール**: https://ollama.ai/
2. **推奨モデル**:
   - `llama3.2:latest` (2GB) - 軽量、高速
   - `llama3:latest` (4.7GB) - バランス型
   - `mistral:latest` (4.1GB) - 代替オプション

3. **Pythonパッケージ**:
```bash
pip install ollama
```

#### 使用方法

```bash
# モデルのダウンロード（初回のみ）
ollama pull llama3.2

# 評価スクリプトの実行
python evaluate_conversions.py
```

#### 評価内容

**注意: 評価のみで自動修正は行いません**

評価観点（スコアリングと問題点の指摘のみ）：

- 文章の流暢性と可読性 (0-100点)
- 技術用語の一貫性 (0-100点)
- 構造の論理性 (0-100点)
- フォーマットの適切性 (0-100点)
- 表の整合性
- 完全性（ページ抽出率、画像数など）

**制限事項**:

- 文章の自動修正機能なし
- 誤字脱字の自動修正なし
- 評価結果を参考に手動で修正が必要

#### 評価結果

結果は以下のファイルに保存されます：
- `output_test/llm_evaluation_results.json` - 詳細データ
- `output_test/llm_quality_report_v2.md` - レポート

#### 環境要件

- **メモリ**: 最低4GB（推奨8GB以上）
- **ディスク**: モデルサイズ + 1GB
- **CPU/GPU**: CPUでも動作可能（GPUがあれば高速）

#### オフライン環境での使用

LLM評価機能は完全にオプションです。Ollamaが利用できない環境では：
- 変換機能は通常通り動作
- 評価スクリプトをスキップ
- 手動での品質確認を推奨

## 開発

### テストの実行

```bash
# 全テストを実行
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html

# 特定のテストのみ
pytest tests/test_parsers.py
```

### プロパティベーステスト

Hypothesisを使用した包括的なテスト：

```bash
# プロパティテストを実行
pytest tests/test_*_properties.py
```

## プロジェクト構造

```
.
├── src/                          # ソースコード
│   ├── cli.py                   # CLIエントリーポイント
│   ├── parsers.py               # ドキュメントパーサー
│   ├── markdown_serializer.py   # Markdown生成
│   ├── image_extractor.py       # 画像抽出
│   ├── text_cleaner.py          # テキストクリーニング
│   ├── llm_evaluator.py         # LLM評価
│   └── ...
├── tests/                        # テストファイル
├── config/                       # 設定ファイル
├── .kiro/specs/                 # 仕様書
├── requirements.txt             # 依存関係
├── setup.py                     # パッケージ設定
└── README.md                    # このファイル
```

## パフォーマンス

- **小規模PDF** (13ページ): 約2.5秒
- **中規模PDF** (58ページ): 約10秒
- **大規模PDF** (212ページ): 約13秒

画像抽出速度: 約28ページ/秒  
ページ処理速度: 約7ページ/秒

## 変換品質

実際のPDFファイルでのテスト結果：

| ファイル | ページ数 | 画像数 | 抽出率 | LLM評価 |
|---------|---------|--------|--------|---------|
| tps653850-q1.pdf | 13 | 11 | 100% | 84.8/100 (B) |
| tcan1463-q1.pdf | 58 | 26 | 100% | 94.4/100 (A) |
| infineon-tle9180d-31qk.pdf | 212 | 23 | 100% | - |

## 要件

- Python 3.9+
- 依存関係は requirements.txt を参照

### オプション

- Tesseract OCR（OCR機能を使用する場合）
- Ollama（LLM評価機能を使用する場合）

## トラブルシューティング

### 画像が抽出されない

```bash
# 画像抽出を明示的に有効化
doc2md -i document.pdf -o output.md --extract-images
```

### エンコーディングエラー

UTF-8で出力されますが、問題がある場合：

```bash
# ログレベルを上げて詳細を確認
doc2md -i document.pdf -o output.md --log-level DEBUG
```

### 大規模PDFの処理

```bash
# ファイルサイズ制限を増やす
doc2md -i large.pdf -o output.md --max-file-size 500
```

## ライセンス

TBD

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 謝辞

- pdfplumber - PDFテキスト抽出
- PyMuPDF - PDF画像抽出
- python-docx - Word文書処理
- openpyxl - Excel処理
- Hypothesis - プロパティベーステスト
- tqdm - 進捗表示
- Ollama - LLM評価
