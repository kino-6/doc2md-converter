# LLM評価機能ガイド

## 概要

LLM評価機能は、変換されたMarkdownの品質を自動的に評価するオプション機能です。Ollamaを使用してローカルLLMで評価を行います。

**重要**: この機能は完全にオプションであり、変換機能とは独立しています。

## 前提条件

### 1. Ollamaのインストール

公式サイトからOllamaをインストールしてください：
https://ollama.ai/

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Windows
公式サイトからインストーラーをダウンロード

### 2. 推奨モデル

| モデル | サイズ | 速度 | 品質 | 推奨用途 |
|--------|--------|------|------|----------|
| llama3.2:latest | 2GB | 高速 | 良好 | 一般的な評価（推奨） |
| llama3:latest | 4.7GB | 中速 | 優秀 | 詳細な評価 |
| mistral:latest | 4.1GB | 中速 | 優秀 | 代替オプション |

### 3. モデルのダウンロード

```bash
# 推奨モデル（軽量）
ollama pull llama3.2

# または高品質モデル
ollama pull llama3

# または代替モデル
ollama pull mistral
```

### 4. Pythonパッケージ

```bash
pip install ollama
```

## 使用方法

### 基本的な使い方

```bash
# 1. まず変換を実行
python src/cli.py -i document.pdf -o output_test/document.md --extract-images

# 2. 評価スクリプトを実行
python evaluate_conversions.py
```

### モデルの指定

環境変数でモデルを指定できます：

```bash
# llama3を使用
OLLAMA_MODEL=llama3:latest python evaluate_conversions.py

# mistralを使用
OLLAMA_MODEL=mistral:latest python evaluate_conversions.py
```

## 評価内容

### 1. 品質評価 (40%の重み付け)

- **流暢性と可読性** (0-100点)
  - 文章の自然さ
  - 読みやすさ
  
- **技術用語の一貫性** (0-100点)
  - 用語の統一性
  - 専門用語の正確性
  
- **構造の論理性** (0-100点)
  - 見出し構造
  - 段落の論理的な流れ
  
- **フォーマットの適切性** (0-100点)
  - Markdown記法の正確性
  - 表や画像の配置

### 2. 表の整合性 (30%の重み付け)

- 列数の一貫性
- 表構造の完全性
- 問題点の検出

### 3. 完全性 (30%の重み付け)

- ページ抽出率
- 画像抽出数
- 表抽出数
- 見出し抽出数

## 評価結果

### 出力ファイル

1. **JSON形式** (`output_test/llm_evaluation_results.json`)
   - 詳細な評価データ
   - プログラムで処理可能

2. **レポート形式** (`output_test/llm_quality_report_v2.md`)
   - 人間が読みやすい形式
   - 改善提案を含む

### 評価グレード

| スコア | グレード | 評価 |
|--------|----------|------|
| 90-100 | A | 優秀 |
| 80-89 | B | 良好 |
| 70-79 | C | 普通 |
| 60-69 | D | 要改善 |
| 0-59 | F | 不合格 |

## 環境要件

### 最小要件

- **CPU**: 2コア以上
- **メモリ**: 4GB以上
- **ディスク**: モデルサイズ + 1GB

### 推奨要件

- **CPU**: 4コア以上（または GPU）
- **メモリ**: 8GB以上
- **ディスク**: 10GB以上

### パフォーマンス

| モデル | 1ファイルあたりの評価時間 |
|--------|--------------------------|
| llama3.2 (CPU) | 約10秒 |
| llama3 (CPU) | 約15秒 |
| llama3.2 (GPU) | 約3秒 |

## トラブルシューティング

### Ollamaサーバーに接続できない

```bash
# Ollamaサーバーを起動
ollama serve
```

別のターミナルで評価スクリプトを実行してください。

### モデルが見つからない

```bash
# モデルをダウンロード
ollama pull llama3.2
```

### メモリ不足

より軽量なモデルを使用してください：

```bash
# 最軽量モデル
ollama pull llama3.2:latest

# または
OLLAMA_MODEL=llama3.2:latest python evaluate_conversions.py
```

### 評価が遅い

1. **GPUを使用**: CUDA対応GPUがあれば自動的に使用されます
2. **軽量モデルを使用**: llama3.2を推奨
3. **評価対象を減らす**: `evaluate_conversions.py`を編集

## オフライン環境での使用

### 事前準備

1. インターネット接続がある環境でモデルをダウンロード
2. モデルファイルをコピー

```bash
# モデルの場所を確認
ollama list

# モデルファイルは通常以下に保存されています
# macOS/Linux: ~/.ollama/models/
# Windows: %USERPROFILE%\.ollama\models\
```

### オフライン環境での実行

モデルファイルをコピー後、通常通り実行できます：

```bash
python evaluate_conversions.py
```

## カスタマイズ

### 評価対象ファイルの変更

`evaluate_conversions.py`を編集：

```python
files = [
    {
        'name': 'my-document',
        'pdf': 'path/to/original.pdf',
        'markdown': 'path/to/converted.md'
    },
    # 追加のファイル...
]
```

### 評価基準の調整

`src/llm_evaluator.py`の`generate_evaluation_report`メソッドで重み付けを変更：

```python
overall_score = (
    quality_eval.get('overall_score', 0) * 0.4 +  # 品質評価の重み
    table_eval.get('consistency_score', 0) * 0.3 +  # 表の整合性の重み
    completeness_eval.get('completeness_score', 0) * 0.3  # 完全性の重み
)
```

## 制限事項

### 大規模PDF

212ページ以上のPDFでは、LLM評価がタイムアウトする可能性があります。

**対策**:
- サンプリング評価（先頭50ページのみ）
- より軽量なモデルの使用

### 評価の主観性

LLMの評価は主観的な要素を含みます。最終的な品質判断は人間が行うことを推奨します。

### 言語サポート

現在、日本語と英語の混在文書に対応していますが、他の言語では評価精度が低下する可能性があります。

## まとめ

LLM評価機能は、変換品質を客観的に測定するための補助ツールです。

- ✅ 完全にオプション
- ✅ 変換機能とは独立
- ✅ オフライン環境でも使用可能
- ✅ カスタマイズ可能

変換機能自体はLLM評価なしでも完全に動作します。
