#!/bin/bash
# Document to Markdown Converter - Environment Setup Script
# このスクリプトは doc2md-converter の環境をセットアップします

set -e  # エラーが発生したら停止

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Document to Markdown Converter${NC}"
echo -e "${BLUE}環境セットアップスクリプト${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# OSの検出
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
    echo -e "${GREEN}✓ macOS を検出しました${NC}"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo -e "${GREEN}✓ Linux を検出しました${NC}"
else
    echo -e "${RED}✗ サポートされていないOS: $OSTYPE${NC}"
    exit 1
fi
echo ""

# uv のインストールチェック
echo -e "${BLUE}[1/6] uv (Python パッケージマネージャー) のチェック${NC}"
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo -e "${GREEN}✓ uv は既にインストールされています: $UV_VERSION${NC}"
else
    echo -e "${YELLOW}  uv がインストールされていません${NC}"
    echo -e "${YELLOW}  uv は高速なPythonパッケージマネージャーです${NC}"
    read -p "  インストールしますか？ (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        echo -e "${YELLOW}  curl -LsSf https://astral.sh/uv/install.sh | sh を実行します...${NC}"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # uvのパスを追加
        export PATH="$HOME/.cargo/bin:$PATH"
        
        if command -v uv &> /dev/null; then
            echo -e "${GREEN}✓ uv のインストールが完了しました${NC}"
        else
            echo -e "${RED}✗ uv のインストールに失敗しました${NC}"
            echo -e "${YELLOW}  手動でインストールしてください: https://docs.astral.sh/uv/${NC}"
            exit 1
        fi
    else
        echo -e "${YELLOW}  スキップしました（pipを使用します）${NC}"
    fi
fi
echo ""

# Python バージョンチェック
echo -e "${BLUE}[2/6] Python バージョンチェック${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ Python $PYTHON_VERSION がインストールされています${NC}"
    
    # Python 3.9以上かチェック
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        echo -e "${GREEN}✓ Python 3.9以上の要件を満たしています${NC}"
    else
        echo -e "${RED}✗ Python 3.9以上が必要です（現在: $PYTHON_VERSION）${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Python3 がインストールされていません${NC}"
    echo -e "${YELLOW}  インストール方法:${NC}"
    if [ "$OS" == "macos" ]; then
        echo -e "${YELLOW}  brew install python@3.11${NC}"
    else
        echo -e "${YELLOW}  sudo apt-get install python3 python3-pip${NC}"
    fi
    exit 1
fi
echo ""

# 仮想環境のセットアップ
echo -e "${BLUE}[3/6] Python 仮想環境のセットアップ${NC}"
if command -v uv &> /dev/null; then
    echo -e "${YELLOW}  uv を使用して仮想環境を作成します...${NC}"
    
    # 既存の仮想環境をチェック
    if [ -d ".venv" ]; then
        echo -e "${GREEN}✓ 仮想環境 (.venv) は既に存在します${NC}"
    else
        echo -e "${YELLOW}  uv venv を実行します...${NC}"
        uv venv
        echo -e "${GREEN}✓ 仮想環境の作成が完了しました${NC}"
    fi
    
    # 仮想環境をアクティベート
    echo -e "${YELLOW}  仮想環境をアクティベートします...${NC}"
    source .venv/bin/activate
    echo -e "${GREEN}✓ 仮想環境がアクティベートされました${NC}"
    echo -e "${CYAN}  Python: $(which python)${NC}"
else
    echo -e "${YELLOW}  uv がインストールされていないため、システムのPythonを使用します${NC}"
    echo -e "${YELLOW}  仮想環境を手動で作成することを推奨します:${NC}"
    echo -e "${YELLOW}    python3 -m venv .venv${NC}"
    echo -e "${YELLOW}    source .venv/bin/activate${NC}"
fi
echo ""

# パッケージのインストール
echo -e "${BLUE}[4/6] Python パッケージのインストール${NC}"
if command -v uv &> /dev/null && [ -d ".venv" ]; then
    echo -e "${YELLOW}  uv pip install -e \".[dev,llm]\" を実行します...${NC}"
    if uv pip install -e ".[dev,llm]"; then
        echo -e "${GREEN}✓ Python パッケージのインストールが完了しました${NC}"
    else
        echo -e "${RED}✗ パッケージのインストールに失敗しました${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}  pip install -e \".[dev,llm]\" を実行します...${NC}"
    if pip install -e ".[dev,llm]"; then
        echo -e "${GREEN}✓ Python パッケージのインストールが完了しました${NC}"
    else
        echo -e "${RED}✗ パッケージのインストールに失敗しました${NC}"
        exit 1
    fi
fi
echo ""

# Tesseract OCR のインストール（オプション）
echo -e "${BLUE}[5/6] Tesseract OCR のインストール（オプション）${NC}"
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version | head -n1)
    echo -e "${GREEN}✓ Tesseract は既にインストールされています: $TESSERACT_VERSION${NC}"
else
    echo -e "${YELLOW}  Tesseract OCR がインストールされていません${NC}"
    read -p "  インストールしますか？ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$OS" == "macos" ]; then
            if command -v brew &> /dev/null; then
                echo -e "${YELLOW}  brew install tesseract tesseract-lang を実行します...${NC}"
                brew install tesseract tesseract-lang
                echo -e "${GREEN}✓ Tesseract のインストールが完了しました${NC}"
            else
                echo -e "${RED}✗ Homebrew がインストールされていません${NC}"
                echo -e "${YELLOW}  手動でインストールしてください: https://brew.sh/${NC}"
            fi
        else
            echo -e "${YELLOW}  sudo apt-get install tesseract-ocr tesseract-ocr-jpn を実行します...${NC}"
            sudo apt-get update
            sudo apt-get install -y tesseract-ocr tesseract-ocr-jpn
            echo -e "${GREEN}✓ Tesseract のインストールが完了しました${NC}"
        fi
    else
        echo -e "${YELLOW}  スキップしました（OCR機能は使用できません）${NC}"
    fi
fi
echo ""

# Ollama のインストール（オプション）
echo -e "${BLUE}[6/6] Ollama のインストール（オプション）${NC}"
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama は既にインストールされています${NC}"
    ollama --version
else
    echo -e "${YELLOW}  Ollama がインストールされていません${NC}"
    echo -e "${YELLOW}  Ollama は文章校正と図→Mermaid変換に必要です${NC}"
    read -p "  インストールしますか？ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ "$OS" == "macos" ]; then
            if command -v brew &> /dev/null; then
                echo -e "${YELLOW}  brew install ollama を実行します...${NC}"
                brew install ollama
                echo -e "${GREEN}✓ Ollama のインストールが完了しました${NC}"
            else
                echo -e "${YELLOW}  手動でインストールしてください: https://ollama.ai/${NC}"
            fi
        else
            echo -e "${YELLOW}  curl -fsSL https://ollama.ai/install.sh | sh を実行します...${NC}"
            curl -fsSL https://ollama.ai/install.sh | sh
            echo -e "${GREEN}✓ Ollama のインストールが完了しました${NC}"
        fi
    else
        echo -e "${YELLOW}  スキップしました（LLM機能は使用できません）${NC}"
    fi
fi
echo ""

# Ollama モデルのダウンロード
if command -v ollama &> /dev/null; then
    echo -e "${BLUE}[7/7] Ollama モデルのダウンロード${NC}"
    
    # llama3.2:latest (文章校正用)
    echo -e "${YELLOW}  llama3.2:latest (2GB) - 文章校正用${NC}"
    if ollama list | grep -q "llama3.2:latest"; then
        echo -e "${GREEN}✓ llama3.2:latest は既にダウンロードされています${NC}"
    else
        read -p "  ダウンロードしますか？ (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}  ollama pull llama3.2:latest を実行します...${NC}"
            ollama pull llama3.2:latest
            echo -e "${GREEN}✓ llama3.2:latest のダウンロードが完了しました${NC}"
        else
            echo -e "${YELLOW}  スキップしました（文章校正機能は使用できません）${NC}"
        fi
    fi
    echo ""
    
    # llama3.2-vision:latest (図変換用)
    echo -e "${YELLOW}  llama3.2-vision:latest (7.9GB) - 図→Mermaid変換用${NC}"
    if ollama list | grep -q "llama3.2-vision"; then
        echo -e "${GREEN}✓ llama3.2-vision:latest は既にダウンロードされています${NC}"
    else
        read -p "  ダウンロードしますか？ (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}  ollama pull llama3.2-vision:latest を実行します...${NC}"
            echo -e "${YELLOW}  注意: 7.9GB のダウンロードには時間がかかります${NC}"
            ollama pull llama3.2-vision:latest
            echo -e "${GREEN}✓ llama3.2-vision:latest のダウンロードが完了しました${NC}"
        else
            echo -e "${YELLOW}  スキップしました（図変換機能は使用できません）${NC}"
        fi
    fi
else
    echo -e "${BLUE}[7/7] Ollama モデルのダウンロード${NC}"
    echo -e "${YELLOW}  Ollama がインストールされていないためスキップします${NC}"
fi
echo ""

# セットアップ完了
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}セットアップが完了しました！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# インストール状況のサマリー
echo -e "${BLUE}インストール状況:${NC}"

if command -v uv &> /dev/null; then
    echo -e "  uv:         ${GREEN}✓${NC}"
else
    echo -e "  uv:         ${YELLOW}✗${NC}"
fi

echo -e "  Python:     ${GREEN}✓${NC}"

if [ -d ".venv" ]; then
    echo -e "  仮想環境:   ${GREEN}✓${NC} (.venv)"
else
    echo -e "  仮想環境:   ${YELLOW}✗${NC}"
fi

echo -e "  パッケージ: ${GREEN}✓${NC}"

if command -v tesseract &> /dev/null; then
    echo -e "  Tesseract:  ${GREEN}✓${NC} (OCR機能が使用可能)"
else
    echo -e "  Tesseract:  ${YELLOW}✗${NC} (OCR機能は使用不可)"
fi

if command -v ollama &> /dev/null; then
    echo -e "  Ollama:     ${GREEN}✓${NC}"
    
    if ollama list | grep -q "llama3.2:latest"; then
        echo -e "    - llama3.2:latest:        ${GREEN}✓${NC} (文章校正が使用可能)"
    else
        echo -e "    - llama3.2:latest:        ${YELLOW}✗${NC} (文章校正は使用不可)"
    fi
    
    if ollama list | grep -q "llama3.2-vision"; then
        echo -e "    - llama3.2-vision:latest: ${GREEN}✓${NC} (図変換が使用可能)"
    else
        echo -e "    - llama3.2-vision:latest: ${YELLOW}✗${NC} (図変換は使用不可)"
    fi
else
    echo -e "  Ollama:     ${YELLOW}✗${NC} (LLM機能は使用不可)"
fi
echo ""

# 使用例
echo -e "${BLUE}使用例:${NC}"

if [ -d ".venv" ]; then
    echo -e "  # 仮想環境をアクティベート（次回以降）"
    echo -e "  ${GREEN}source .venv/bin/activate${NC}"
    echo ""
fi

echo -e "  # 基本的な変換"
echo -e "  ${GREEN}doc2md -i document.pdf -o output.md${NC}"
echo ""
echo -e "  # フル機能モード（推奨）"
echo -e "  ${GREEN}doc2md -i document.pdf -o output.md --full${NC}"
echo ""
echo -e "  # ヘルプを表示"
echo -e "  ${GREEN}doc2md --help${NC}"
echo ""

if [ -d ".venv" ]; then
    echo -e "${CYAN}注意: 次回このプロジェクトを使用する際は、以下のコマンドで仮想環境をアクティベートしてください:${NC}"
    echo -e "${CYAN}  source .venv/bin/activate${NC}"
    echo ""
fi

echo -e "${BLUE}詳細は README.md を参照してください${NC}"
echo ""
