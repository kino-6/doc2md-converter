# クイックリファレンス

## インストール

```bash
pip install dist/doc2md_converter-1.0.0-py3-none-any.whl
```

## 基本的な使い方

```bash
# 単一ファイル変換
doc2md -i document.pdf -o output.md

# 画像抽出を有効化
doc2md -i document.pdf -o output.md --extract-images

# バッチ変換
doc2md -i file1.docx -i file2.xlsx -i file3.pdf
```

## よく使うオプション

| オプション | 説明 | 例 |
|-----------|------|-----|
| `-i, --input` | 入力ファイル（必須） | `-i document.pdf` |
| `-o, --output` | 出力ファイル | `-o output.md` |
| `--extract-images` | 画像抽出を有効化 | `--extract-images` |
| `--preview` | プレビューモード（最初の50行） | `--preview` |
| `--dry-run` | ファイル出力なし | `--dry-run` |
| `-c, --config` | 設定ファイル | `-c config.yaml` |
| `--log-level` | ログレベル | `--log-level DEBUG` |

## 設定ファイル例

```yaml
# config.yaml
extract_images: true
include_metadata: true
heading_offset: 0
ocr_lang: "eng+jpn"
max_file_size_mb: 100
```

## LLM評価（オプション）

**注意**: 品質評価のみで、文章の自動修正は行いません。

```bash
# Ollamaモデルをダウンロード
ollama pull llama3.2

# 評価スクリプトを実行（スコアリングのみ）
python evaluate_conversions.py

# 結果を確認
cat output_test/llm_quality_report_v2.md
```

**制限事項**:
- 文章の自動修正機能なし
- 誤字脱字の自動修正なし
- 評価結果を参考に手動で修正が必要

## トラブルシューティング

### doc2md: command not found

```bash
# PATHを確認
which doc2md

# PIPのbinディレクトリを追加
export PATH="$HOME/.local/bin:$PATH"
```

### Tesseract not found

```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

### 画像が抽出されない

```bash
# 画像抽出を明示的に有効化
doc2md -i document.pdf -o output.md --extract-images
```

## パフォーマンス

- 小規模PDF (13ページ): ~2.5秒
- 中規模PDF (58ページ): ~10秒
- 大規模PDF (212ページ): ~13秒
- 画像抽出速度: ~28ページ/秒
- ページ処理速度: ~7ページ/秒

## サポートされるフォーマット

| フォーマット | 拡張子 | テキスト | 表 | 画像 | 見出し |
|------------|--------|---------|-----|------|--------|
| Word       | .docx  | ✅      | ✅  | ✅   | ✅     |
| Excel      | .xlsx  | ✅      | ✅  | ❌   | ✅     |
| PDF        | .pdf   | ✅      | ✅  | ✅   | ✅     |

## ヘルプ

```bash
# ヘルプを表示
doc2md --help

# バージョンを表示
doc2md --version
```
