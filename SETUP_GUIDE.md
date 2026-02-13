# doc2md-converter セットアップガイド

## クイックスタート（推奨）

最も簡単な方法は、自動セットアップスクリプトを使用することです：

```bash
# リポジトリをクローン
git clone https://github.com/kino-6/doc2md-converter.git
cd doc2md-converter

# 自動セットアップを実行
./setup.sh
```

このスクリプトは対話式で、以下を自動的に行います：

1. ✅ **uv のインストール** - 高速Pythonパッケージマネージャー（オプション）
2. ✅ **Python 仮想環境の作成** - `.venv` ディレクトリに隔離された環境を作成
3. ✅ **Python バージョンチェック** - Python 3.9以上が必要
4. ✅ **パッケージのインストール** - 必要な全てのPythonパッケージ
5. ✅ **Tesseract OCR** - OCR機能用（オプション）
6. ✅ **Ollama** - LLM機能用（オプション）
7. ✅ **LLMモデル** - 文章校正と図変換用（オプション）

## 次回以降の使用

セットアップ後、次回プロジェクトを使用する際は：

```bash
cd doc2md-converter

# 仮想環境をアクティベート
source .venv/bin/activate

# コマンドを実行
doc2md -i document.pdf -o output.md --full
```

## 手動セットアップ

自動スクリプトを使用しない場合の手順：

### 方法1: uv を使用（推奨）

```bash
# 1. uv をインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. リポジトリをクローン
git clone https://github.com/kino-6/doc2md-converter.git
cd doc2md-converter

# 3. 仮想環境を作成
uv venv

# 4. 仮想環境をアクティベート
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# 5. パッケージをインストール
uv pip install -e ".[dev,llm]"
```

### 方法2: pip を使用

```bash
# 1. リポジトリをクローン
git clone https://github.com/kino-6/doc2md-converter.git
cd doc2md-converter

# 2. 仮想環境を作成
python3 -m venv .venv

# 3. 仮想環境をアクティベート
source .venv/bin/activate  # macOS/Linux
# または
.venv\Scripts\activate  # Windows

# 4. パッケージをインストール
pip install -e ".[dev,llm]"
```

## オプション機能のセットアップ

### Tesseract OCR（OCR機能用）

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-jpn
```

**Windows:**
- https://github.com/UB-Mannheim/tesseract/wiki からインストーラーをダウンロード

### Ollama（LLM機能用）

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
- https://ollama.ai/ からインストーラーをダウンロード

**モデルのダウンロード:**
```bash
# 文章校正用（2GB）
ollama pull llama3.2:latest

# 図→Mermaid変換用（7.9GB）
ollama pull llama3.2-vision:latest
```

## 使用例

### 基本的な変換

```bash
doc2md -i document.pdf -o output.md
```

### フル機能モード（推奨）

すべての機能を有効化：

```bash
doc2md -i document.pdf -o output.md --full
```

これは以下と同等です：

```bash
doc2md -i document.pdf -o output.md \
  --extract-images \
  --proofread \
  --diagram-to-mermaid
```

### 機能別の使用

```bash
# 画像抽出のみ
doc2md -i document.pdf -o output.md --extract-images

# 文章校正のみ
doc2md -i document.pdf -o output.md --proofread

# インタラクティブ校正
doc2md -i document.pdf -o output.md --proofread --proofread-mode interactive

# 図→Mermaid変換
doc2md -i document.pdf -o output.md --extract-images --diagram-to-mermaid
```

### バッチ処理

```bash
# 複数ファイルを一括変換
doc2md -i file1.pdf -i file2.docx -i file3.xlsx --full
```

## 機能と前提条件

| 機能 | 必須ツール | モデル | サイズ | デフォルト |
|------|-----------|--------|--------|-----------|
| 基本変換 | なし | - | - | ✅ |
| 画像抽出 | なし | - | - | ✅ |
| OCR | Tesseract | - | ~100MB | ❌ |
| 文章校正 | Ollama | llama3.2:latest | 2GB | ❌ |
| 図→Mermaid | Ollama | llama3.2-vision:latest | 7.9GB | ❌ |

## トラブルシューティング

### セットアップがうまくいかない

```bash
# セットアップスクリプトを再実行
./setup.sh

# または各コンポーネントを個別に確認
python3 --version  # Python 3.9以上が必要
pip list | grep doc2md-converter
tesseract --version  # OCR用（オプション）
ollama --version  # LLM用（オプション）
```

### 仮想環境が見つからない

```bash
# 仮想環境を再作成
uv venv
# または
python3 -m venv .venv

# アクティベート
source .venv/bin/activate
```

### Ollamaに接続できない

```bash
# Ollamaが起動しているか確認
ollama list

# モデルがダウンロードされているか確認
ollama pull llama3.2
ollama pull llama3.2-vision
```

### パッケージのインストールエラー

```bash
# pip をアップグレード
pip install --upgrade pip

# 再インストール
pip install -e ".[dev,llm]"
```

### 処理が遅い

- **文章校正**: より軽量なモデルを使用
  ```bash
  doc2md -i document.pdf -o output.md --proofread --proofread-model llama3.2:latest
  ```

- **図変換**: 大きな図が多い場合は時間がかかります（1画像あたり5-15秒）

### メモリ不足

- llama3.2-vision (7.9GB) は約8GBのメモリが必要です
- 代替として llava:latest (4.7GB) を使用:
  ```bash
  doc2md -i document.pdf -o output.md --full --diagram-model llava:latest
  ```

## 環境変数

以下の環境変数でカスタマイズ可能：

```bash
# Ollama のホスト（デフォルト: http://localhost:11434）
export OLLAMA_HOST=http://localhost:11434

# ログレベル
export DOC2MD_LOG_LEVEL=DEBUG
```

## アンインストール

```bash
# 仮想環境を削除
rm -rf .venv

# パッケージをアンインストール
pip uninstall doc2md-converter

# リポジトリを削除
cd ..
rm -rf doc2md-converter
```

## サポート

- GitHub Issues: https://github.com/kino-6/doc2md-converter/issues
- README: [README.md](README.md)
- 実装詳細: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)

## ライセンス

TBD
