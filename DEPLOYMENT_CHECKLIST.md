# デプロイメントチェックリスト

## ✅ 完了済み

### コード実装
- [x] すべての機能実装完了（29タスク）
- [x] プロパティベーステスト実装（53テスト）
- [x] 統合テスト実装
- [x] エンドツーエンドテスト実装
- [x] 実ファイル検証完了

### パッケージング
- [x] `setup.py` 設定完了
- [x] `requirements.txt` 更新
- [x] `MANIFEST.in` 作成
- [x] パッケージビルド成功
  - [x] `doc2md_converter-1.0.0-py3-none-any.whl` (53KB)
  - [x] `doc2md_converter-1.0.0.tar.gz` (47KB)

### ドキュメント
- [x] `README.md` - 包括的な使用ガイド
- [x] `INSTALLATION.md` - インストール手順
- [x] `RELEASE_NOTES.md` - リリースノート
- [x] `docs/LLM_EVALUATION.md` - LLM評価ガイド
- [x] `PROJECT_SUMMARY.md` - プロジェクトサマリー
- [x] `build_package.sh` - ビルドスクリプト

### 設定
- [x] `.gitignore` 更新
  - [x] `output*/` 除外
  - [x] `docs_target*/` 除外
  - [x] テストスクリプト除外

## 📋 次のステップ（オプション）

### Gitリポジトリの初期化

```bash
# Gitリポジトリを初期化
git init

# すべてのファイルを追加
git add .

# 初回コミット
git commit -m "Initial commit: Document to Markdown Converter v1.0.0"

# リモートリポジトリを追加（例）
git remote add origin https://github.com/username/doc2md-converter.git
git push -u origin main
```

### ローカルインストールテスト

```bash
# 仮想環境を作成（推奨）
python -m venv test_env
source test_env/bin/activate  # Windows: test_env\Scripts\activate

# パッケージをインストール
pip install dist/doc2md_converter-1.0.0-py3-none-any.whl

# CLIコマンドをテスト
doc2md --help

# サンプル変換を実行
doc2md -i docs_target/tps65053.pdf -o test_output.md --extract-images

# 仮想環境を終了
deactivate
```

### PyPIへの公開（オプション）

```bash
# Twineをインストール
pip install twine

# パッケージを検証
twine check dist/*

# TestPyPIにアップロード（テスト用）
twine upload --repository testpypi dist/*

# 本番PyPIにアップロード
twine upload dist/*
```

### CI/CDセットアップ（オプション）

GitHub Actionsの設定例：

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -e ".[dev]"
      - run: pytest tests/
```

## 🔍 検証項目

### 機能テスト

```bash
# Word変換
doc2md -i sample.docx -o output.md

# Excel変換
doc2md -i sample.xlsx -o output.md

# PDF変換（画像抽出あり）
doc2md -i sample.pdf -o output.md --extract-images

# バッチ変換
doc2md -i file1.docx -i file2.xlsx -i file3.pdf

# 設定ファイル使用
doc2md -i sample.pdf -c config.yaml

# プレビューモード
doc2md -i sample.pdf --preview

# Dry-runモード
doc2md -i sample.pdf --dry-run
```

### LLM評価テスト（オプション）

**注意**: LLM評価は品質スコアリングのみで、文章の自動修正は行いません。

```bash
# Ollamaが起動していることを確認
ollama list

# 評価スクリプトを実行
python evaluate_conversions.py

# 結果を確認（評価スコアと問題点の指摘のみ）
cat output_test/llm_quality_report_v2.md
```

## 📊 品質メトリクス

### コードカバレッジ

```bash
# カバレッジを測定
pytest --cov=src --cov-report=html

# レポートを確認
open htmlcov/index.html
```

### パフォーマンステスト

```bash
# 大規模PDFでテスト
time doc2md -i large_document.pdf -o output.md --extract-images
```

## 🚀 本番環境デプロイ

### システム要件

- Python 3.9+
- Tesseract OCR（OCR機能を使用する場合）
- Ollama（LLM評価を使用する場合）

### インストール手順

```bash
# パッケージをインストール
pip install doc2md-converter

# または Wheelファイルから
pip install doc2md_converter-1.0.0-py3-none-any.whl

# Tesseract OCRをインストール（オプション）
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-jpn

# Ollamaをインストール（オプション）
# https://ollama.ai/ からダウンロード
```

## 📝 リリースノート

バージョン 1.0.0 の主な機能：

- Word、Excel、PDF文書のMarkdown変換
- 画像抽出（埋め込み画像 + ベクターグラフィック）
- OCR機能（多言語対応）
- バッチ変換
- 進捗表示（tqdm）
- LLM品質評価（オプション、評価のみで自動修正なし）
- 包括的なエラーハンドリング
- UTF-8エンコーディング対応

## ✅ 最終確認

- [x] すべてのテストが成功
- [x] パッケージビルドが成功
- [x] ドキュメントが完備
- [x] `.gitignore` が適切に設定
- [x] 実ファイルで検証済み
- [x] LLM評価が動作確認済み

## 🎉 プロジェクト完了

すべての準備が整いました。パッケージは本番環境で使用可能です！
