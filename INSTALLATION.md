# インストールガイド

## パッケージのビルド

```bash
# ビルドスクリプトを実行
./build_package.sh

# または手動でビルド
python setup.py sdist bdist_wheel
```

## インストール

### ローカルインストール（開発用）

```bash
# 編集可能モードでインストール
pip install -e .

# 開発依存関係を含む
pip install -e ".[dev]"

# LLM評価機能を含む
pip install -e ".[dev,llm]"
```

### ビルド済みパッケージからインストール

```bash
# Wheelファイルからインストール
pip install dist/doc2md_converter-1.0.0-py3-none-any.whl

# または tar.gz から
pip install dist/doc2md_converter-1.0.0.tar.gz
```

## インストール確認

```bash
# CLIコマンドが利用可能か確認
doc2md --help

# バージョン確認
python -c "import src; print('インストール成功')"
```

## 依存関係

### 必須

- Python 3.9+
- python-docx>=0.8.11
- openpyxl>=3.1.0
- PyPDF2>=3.0.0
- pdfplumber>=0.10.0
- PyMuPDF>=1.23.0
- pytesseract>=0.3.10
- PyYAML>=6.0
- click>=8.1.0
- markdown-it-py>=3.0.0
- tqdm>=4.65.0

### オプション

#### OCR機能を使用する場合

Tesseract OCRエンジンのインストールが必要です：

```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-jpn

# Windows
# https://github.com/UB-Mannheim/tesseract/wiki からインストーラーをダウンロード
```

#### LLM評価機能を使用する場合

```bash
# Ollamaのインストール
# https://ollama.ai/ からダウンロード

# モデルのダウンロード
ollama pull llama3.2

# Pythonパッケージ
pip install ollama
```

## アンインストール

```bash
pip uninstall doc2md-converter
```

## トラブルシューティング

### ImportError: No module named 'src'

パッケージが正しくインストールされていません。再インストールしてください：

```bash
pip uninstall doc2md-converter
pip install dist/doc2md_converter-1.0.0-py3-none-any.whl
```

### doc2md: command not found

PIPのbinディレクトリがPATHに含まれていません：

```bash
# PATHを確認
echo $PATH

# PIPのbinディレクトリを追加（例）
export PATH="$HOME/.local/bin:$PATH"
```

### Tesseract not found

Tesseract OCRがインストールされていないか、PATHに含まれていません：

```bash
# インストール確認
tesseract --version

# macOSの場合、PATHを設定
export PATH="/opt/homebrew/bin:$PATH"
```
