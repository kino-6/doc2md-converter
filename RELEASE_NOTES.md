# Document to Markdown Converter v1.0.0 - リリースノート

リリース日: 2026-02-13

## 概要

Word、Excel、PDFドキュメントを高品質なMarkdownに変換するCLIツールの初回リリースです。

## 主要機能

### ドキュメント変換

- ✅ **Word (.docx)**: テキスト、表、画像、見出し、リスト、リンクを完全サポート
- ✅ **Excel (.xlsx)**: 全シート、数式、結合セル、ハイパーリンク、日時フォーマットをサポート
- ✅ **PDF (.pdf)**: テキスト、表、画像（埋め込み＋ベクターグラフィック）を抽出

### 画像処理

- 埋め込み画像の自動抽出（JPEG、PNG、GIF）
- ベクターグラフィックの自動検出とPNG化（144 DPI）
- Base64埋め込みオプション
- 画像参照の自動生成

### ユーザーエクスペリエンス

- tqdmによる進捗バー表示
- 詳細なログ出力
- プレビューモード
- ドライランモード
- バッチ処理対応

### 品質保証

- UTF-8エンコーディング対応
- テキストクリーニング（孤立文字削除、改行修正）
- Markdown検証
- エラーハンドリング

### 評価機能（オプション）

- Ollamaによる変換品質の自動評価
- 流暢性、一貫性、構造、フォーマットの評価
- 表の整合性チェック
- 完全性評価（ページ抽出率、画像数など）

## パフォーマンス

### 処理速度

- 画像抽出: 約28ページ/秒
- ページ処理: 約7ページ/秒
- 小規模PDF (13ページ): 2.5秒
- 中規模PDF (58ページ): 10秒
- 大規模PDF (212ページ): 13秒

### 変換品質

実際のPDFファイルでのテスト結果：

| ファイル | ページ数 | 画像数 | 抽出率 | LLM評価 |
|---------|---------|--------|--------|---------|
| tps653850-q1.pdf | 13 | 11 | 100% | 84.8/100 (B) |
| tcan1463-q1.pdf | 58 | 26 | 100% | 94.4/100 (A) |
| infineon-tle9180d-31qk.pdf | 212 | 23 | 100% | - |

## テストカバレッジ

- **ユニットテスト**: 25個以上
- **プロパティベーステスト**: 50個以上のプロパティ
- **統合テスト**: エンドツーエンドテスト含む
- **カバレッジ**: 主要モジュールで80%以上

## 技術スタック

### コア依存関係

- python-docx: Word文書処理
- openpyxl: Excel処理
- PyPDF2: PDF基本処理
- pdfplumber: PDFテキスト抽出
- PyMuPDF (fitz): PDF画像抽出
- click: CLIフレームワーク
- tqdm: 進捗表示

### テスト

- pytest: テストフレームワーク
- hypothesis: プロパティベーステスト
- pytest-cov: カバレッジ測定

### オプション

- pytesseract: OCR機能（未実装）
- ollama: LLM評価

## インストール

```bash
# 基本インストール
pip install doc2md-converter

# 開発環境
pip install doc2md-converter[dev]

# LLM評価機能を含む
pip install doc2md-converter[dev,llm]
```

## 使用例

```bash
# 基本的な変換
doc2md -i document.pdf -o output.md --extract-images

# バッチ処理
doc2md -i file1.docx -i file2.xlsx -i file3.pdf

# 設定ファイルを使用
doc2md -i document.pdf -c config.yaml

# プレビューモード
doc2md -i document.pdf --preview
```

## 既知の制限事項

### PDFテキスト抽出

- 複雑なレイアウトのPDFでは改行位置が不適切になる場合がある
- これはpdfplumberの制限によるもの
- TextCleanerモジュールで部分的に改善

### OCR機能

- 基本的な実装は完了しているが、本格的な統合は未実装
- 将来のバージョンで改善予定

### 大規模PDFのLLM評価

- 212ページ以上のPDFではLLM評価がタイムアウトする可能性
- サンプリング戦略の実装が必要

## 今後の改善予定

1. **OCR統合**: Tesseract OCRの完全統合
2. **テキスト品質向上**: LLMによる後処理
3. **表処理改善**: 複雑な表構造の処理
4. **大規模PDF対応**: LLM評価のサンプリング戦略
5. **追加フォーマット**: PowerPoint (.pptx) サポート

## 変更履歴

### v1.0.0 (2026-02-13)

- 初回リリース
- Word、Excel、PDF変換機能
- 画像抽出機能
- 進捗表示機能
- LLM評価機能（オプション）
- テキストクリーニング機能
- 包括的なテストスイート

## 貢献者

- Document Converter Team

## ライセンス

TBD

## サポート

問題や質問がある場合は、GitHubのissueを開いてください。

## 謝辞

このプロジェクトは以下のオープンソースプロジェクトに依存しています：

- pdfplumber
- PyMuPDF
- python-docx
- openpyxl
- Hypothesis
- tqdm
- Ollama

全ての貢献者とメンテナーに感謝します。
