#!/bin/bash
# Document to Markdown Converter - Environment Setup Script
# このスクリプトは doc2md-converter の環境をセットアップします

set -e  # エラーが発生したら停止

# 色付き出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Python バージョンチェック
echo -e "${BLUE}[1/5] Python バージョンチェック${NC}"
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

# パッケージのインストール
echo -e "${BLUE}[2/5] Python パッケージのインストール${NC}"
echo -e "${YELLOW}  pip install -e \".[dev,llm]\" を実行します...${NC}"
if pip install -e ".[dev,llm]"; then
    echo -e "${GREEN}✓ Python パッケージのインストールが完了しました${NC}"
else
    echo -e "${RED}✗ パッケージのインストールに失敗しました${NC}"
    exit 1
fi
echo ""

# Tesseract OCR のインストール（オプション）
echo -e "${BLUE}[3/5] Tesseract OCR のインストール（オプション）${NC}"
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
echo -e "${BLUE}[4/5] Ollama のインストール（オプション）${NC}"
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
    echo -e "${BLUE}[5/5] Ollama モデルのダウンロード${NC}"
    
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
    echo -e "${BLUE}[5/5] Ollama モデルのダウンロード${NC}"
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
echo -e "  Python:     ${GREEN}✓${NC}"
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
echo -e "  # 基本的な変換"
echo -e "  ${GREEN}doc2md -i document.pdf -o output.md${NC}"
echo ""
echo -e "  # フル機能モード（推奨）"
echo -e "  ${GREEN}doc2md -i document.pdf -o output.md --full${NC}"
echo ""
echo -e "  # ヘルプを表示"
echo -e "  ${GREEN}doc2md --help${NC}"
echo ""

echo -e "${BLUE}詳細は README.md を参照してください${NC}"
echo ""
