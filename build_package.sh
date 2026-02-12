#!/bin/bash
# パッケージビルドスクリプト

set -e

echo "Document to Markdown Converter - パッケージビルド"
echo "================================================"
echo ""

# クリーンアップ
echo "1. 既存のビルドファイルをクリーンアップ..."
rm -rf build/ dist/ *.egg-info/
echo "   完了"
echo ""

# テストの実行
echo "2. テストを実行..."
pytest tests/ -v --tb=short
echo "   完了"
echo ""

# パッケージのビルド
echo "3. パッケージをビルド..."
python setup.py sdist bdist_wheel
echo "   完了"
echo ""

# ビルド結果の表示
echo "4. ビルド結果:"
ls -lh dist/
echo ""

echo "================================================"
echo "ビルド完了！"
echo ""
echo "インストール方法:"
echo "  pip install dist/doc2md_converter-1.0.0-py3-none-any.whl"
echo ""
echo "PyPIへのアップロード:"
echo "  twine upload dist/*"
echo ""
