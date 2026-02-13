# LLM文章校正機能 - 実装サマリー

## 概要

Task 30で実装されたLLMによる文章修正・校正機能は、Ollamaを使用してMarkdownテキストを自動的に校正します。

## 実装されたコンポーネント

### 1. TextProofreader クラス (`src/text_proofreader.py`)

**機能**:
- Markdownテキストの校正
- 誤字脱字の検出と修正
- 文法エラーの検出と修正
- 不自然な改行の修正
- 孤立文字の統合
- 技術用語の一貫性チェック
- 修正前後の差分生成

**主要メソッド**:
- `proofread()`: テキストを校正
- `proofread_ocr_text()`: OCR抽出テキストを校正
- `check_terminology_consistency()`: 技術用語の一貫性をチェック

### 2. ProofreadModeHandler クラス (`src/proofread_modes.py`)

**機能**:
- 3つの校正モードをサポート:
  - **AUTO**: 自動修正（確認なしで適用）
  - **INTERACTIVE**: インタラクティブ（修正案を表示して確認）
  - **DRY_RUN**: Dry-run（修正案のみ表示）
- 修正履歴の記録と管理

**主要クラス**:
- `ProofreadMode`: 校正モードの列挙型
- `ProofreadHistory`: 修正履歴を管理
- `ProofreadModeHandler`: 校正モードを処理

### 3. OCRProofreader クラス (`src/ocr_proofreader.py`)

**機能**:
- OCR特有のエラーの自動修正
- 技術文書特有の用語の修正
- 数値・記号の正確性向上
- ルールベースとLLMベースの修正を組み合わせ

**修正パターン**:
- 文字の混同（l/I、0/O、rn/m など）
- 技術用語の誤認識（APl→API、l/O→I/O など）
- 数値内のスペース修正
- 小数点の修正
- 単位とのスペース正規化

### 4. CLI統合 (`src/cli.py`)

**追加されたオプション**:
- `--proofread`: 校正を有効化
- `--proofread-mode`: 校正モード（auto/interactive/dry-run）
- `--proofread-model`: 使用するLLMモデル
- `--proofread-output`: 校正結果の保存先

### 5. 設定管理 (`src/config.py`)

**追加された設定項目**:
- `enable_proofread`: 校正の有効化
- `proofread_mode`: 校正モード
- `proofread_model`: LLMモデル
- `proofread_output_path`: 校正結果の出力パス

## 使用例

### 基本的な使用

```bash
# 自動モード（確認なしで全て適用）
doc2md -i document.pdf -o output.md --proofread

# インタラクティブモード（各修正を確認）
doc2md -i document.pdf -o output.md --proofread --proofread-mode interactive

# Dry-runモード（修正案のみ表示）
doc2md -i document.pdf --proofread --proofread-mode dry-run

# 特定のモデルを使用
doc2md -i document.pdf -o output.md --proofread --proofread-model llama3:latest

# 校正結果を別ファイルに保存
doc2md -i document.pdf -o output.md --proofread --proofread-output corrected.md
```

### バッチ処理

```bash
# 複数ファイルに校正を適用
doc2md -i file1.pdf -i file2.pdf -i file3.pdf --proofread
```

## テスト

実装されたテスト (`tests/test_proofreading.py`):

- TextProofreaderのテスト（5テスト）
- OCRProofreaderのテスト（7テスト）
- ProofreadModesのテスト（4テスト）
- ProofreadHistoryのテスト（2テスト）
- ProofreadingResultのテスト（2テスト）

**テスト結果**: 全20テスト成功 ✅

## ドキュメント

README.mdに以下のセクションを追加:

1. **特徴**: LLM文章校正機能の追加
2. **使用方法**: 校正オプションの使用例
3. **LLM文章校正機能**: 詳細な機能説明
   - 機能概要
   - 前提条件
   - 使用方法（3つのモード）
   - 校正の重点領域
   - 使用例
   - ベストプラクティス
   - 制限事項と注意点
   - 修正履歴
   - トラブルシューティング
   - 環境要件

## 技術的な詳細

### アーキテクチャ

```
CLI (cli.py)
  ↓
ConversionOrchestrator
  ↓
Markdown Output
  ↓
ProofreadModeHandler (proofread_modes.py)
  ↓
TextProofreader (text_proofreader.py)
  ├─ 通常テキスト校正
  └─ OCRProofreader (ocr_proofreader.py)
      ├─ ルールベース修正
      └─ LLMベース修正
```

### データフロー

1. ユーザーが `--proofread` オプションを指定
2. 変換が完了し、Markdownが生成される
3. ProofreadModeHandlerが指定されたモードで処理
4. TextProofreaderがLLMを使用してテキストを解析
5. OCRテキストの場合、OCRProofreaderが追加処理
6. 修正結果を適用（モードに応じて）
7. 履歴に記録

### LLM統合

- **使用ライブラリ**: `ollama` Python クライアント
- **デフォルトモデル**: `llama3.2:latest`
- **JSON形式**: LLMレスポンスはJSON形式で取得
- **エラーハンドリング**: LLM呼び出し失敗時は元のテキストを返す

## 制限事項

1. **Ollama必須**: Ollamaがインストールされている必要がある
2. **処理時間**: LLMを使用するため、通常の変換より時間がかかる
3. **精度**: LLMの性能に依存
4. **オフライン不可**: インターネット接続は不要だが、Ollamaが必要

## 今後の拡張可能性

- [ ] カスタム校正ルールの追加
- [ ] 複数のLLMプロバイダーのサポート
- [ ] 校正品質のメトリクス
- [ ] 言語別の校正ルール
- [ ] 校正結果の統計レポート

## まとめ

Task 30の実装により、doc2mdは以下の機能を獲得しました:

✅ 誤字脱字の自動修正
✅ 文法エラーの修正
✅ OCR結果の品質向上
✅ 3つの校正モード（自動/インタラクティブ/Dry-run）
✅ 修正履歴の記録
✅ CLI統合
✅ 包括的なテスト
✅ 詳細なドキュメント

これにより、ユーザーは変換後のMarkdownテキストを自動的に校正し、品質を向上させることができます。
