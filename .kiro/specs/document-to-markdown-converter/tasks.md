# Implementation Plan: Document to Markdown Converter

## Overview

このプランは、Word、Excel、PDFファイルをMarkdownに変換するCLIツールを段階的に実装します。Phase 1でMVPを構築し、その後機能を拡張していきます。各タスクは前のタスクの成果物を基に構築され、最終的に完全に統合されたシステムとなります。

## Tasks

- [x] 1. プロジェクト構造とコア基盤のセットアップ
  - プロジェクトディレクトリ構造を作成（src/, tests/, config/）
  - 依存関係管理ファイルを作成（requirements.txt, setup.py）
  - 基本的なロギング設定を実装
  - テストフレームワーク（pytest, Hypothesis）をセットアップ
  - _Requirements: 10.1, 10.5_

- [x] 2. データモデルと内部表現の実装
  - [x] 2.1 内部ドキュメント構造のデータクラスを実装
    - InternalDocument, Section, ContentBlock, Heading, Paragraph, Table, List, ImageReference クラスを作成
    - 各クラスに適切な型ヒントとdocstringを追加
    - _Requirements: 12.1_
  
  - [x] 2.2 内部表現のプロパティテストを作成
    - **Property 50: Document parsing**
    - **Validates: Requirements 12.1**

- [x] 3. ファイル検証とルーティングの実装
  - [x] 3.1 FileValidator クラスを実装
    - ファイル存在確認、形式検証、サイズチェック、読み取り可能性確認のメソッドを実装
    - _Requirements: 4.1, 4.2, 4.4_
  
  - [x] 3.2 ファイル検証のプロパティテストを作成
    - **Property 18: Invalid format error handling**
    - **Property 19: Corrupted file error handling**
    - **Property 20: File size limit enforcement**
    - **Validates: Requirements 4.1, 4.2, 4.4**
  
  - [x] 3.3 FormatRouter クラスを実装
    - ファイル拡張子に基づいてパーサーを選択するロジックを実装
    - _Requirements: 1.1, 2.1, 3.1_

- [x] 4. Word文書パーサーの実装
  - [x] 4.1 WordParser クラスの基本構造を実装
    - python-docx を使用してWord文書を読み込む
    - テキストコンテンツを抽出して内部表現に変換
    - _Requirements: 1.1_
  
  - [x] 4.2 テキスト抽出のプロパティテストを作成
    - **Property 1: Text content extraction**
    - **Validates: Requirements 1.1**
  
  - [x] 4.3 見出し、リスト、表の抽出機能を追加
    - 見出しレベルの検出と変換
    - 順序付き/順序なしリストの構造保持
    - 表のヘッダーと行データの抽出
    - _Requirements: 1.2, 1.3, 1.4_
  
  - [x] 4.4 構造要素のプロパティテストを作成
    - **Property 2: Heading level mapping**
    - **Property 3: List structure preservation**
    - **Property 4: Table conversion**
    - **Validates: Requirements 1.2, 1.3, 1.4, 5.5**
  
  - [x] 4.5 書式とリンクの抽出機能を追加
    - 太字、斜体の検出と保持
    - ハイパーリンクの抽出
    - 画像参照の抽出（画像処理は後のフェーズ）
    - _Requirements: 1.5, 1.6, 1.7_
  
  - [x] 4.6 書式とリンクのプロパティテストを作成
    - **Property 5: Text formatting preservation**
    - **Property 6: Image extraction and referencing**
    - **Property 7: Hyperlink preservation**
    - **Validates: Requirements 1.5, 1.6, 1.7**

- [x] 5. Markdownシリアライザーの実装
  - [x] 5.1 MarkdownSerializer クラスを実装
    - 内部表現からMarkdown構文への変換メソッドを実装
    - 見出し、段落、リスト、表、画像、リンクのシリアライズ
    - _Requirements: 12.2, 5.4_
  
  - [x] 5.2 Markdownシリアライズのプロパティテストを作成
    - **Property 51: Markdown serialization**
    - **Property 25: Valid Markdown generation**
    - **Validates: Requirements 12.2, 5.4**
  
  - [x] 5.3 PrettyPrinter クラスを実装
    - 空白の正規化、表の列揃え、適切な改行の挿入
    - _Requirements: 12.3, 5.2, 5.5_
  
  - [x] 5.4 Pretty printing のプロパティテストを作成
    - **Property 52: Pretty printing consistency**
    - **Property 23: Spacing and readability**
    - **Validates: Requirements 12.3, 5.2**
  
  - [x] 5.5 特殊文字のエスケープ処理を実装
    - Markdown特殊文字の適切なエスケープ
    - _Requirements: 5.3, 9.3_
  
  - [x] 5.6 特殊文字処理のプロパティテストを作成
    - **Property 24: Special character handling**
    - **Validates: Requirements 5.3, 9.3**

- [x] 6. Checkpoint - コア変換機能の検証
  - すべてのテストが成功することを確認
  - Word文書からMarkdownへの基本的な変換が動作することを確認
  - 質問があればユーザーに確認

- [x] 7. CLI インターフェースの実装
  - [x] 7.1 CLIInterface クラスを実装
    - argparse または Click を使用してコマンドライン引数を解析
    - 主要オプション（--input, --output, --config, --preview, --dry-run, --log-level）を実装
    - _Requirements: 6.1_
  
  - [x] 7.2 CLI インターフェースの統合テストを作成
    - コマンドライン引数の解析テスト
    - ヘルプ表示のテスト
    - _Requirements: 6.1_
  
  - [x] 7.3 ConversionOrchestrator クラスを実装
    - 変換プロセス全体を調整するメインロジック
    - エラーハンドリングと進捗管理
    - _Requirements: 4.5, 5.1_
  
  - [x] 7.4 Orchestrator のプロパティテストを作成
    - **Property 21: Graceful degradation**
    - **Property 22: Structure preservation**
    - **Validates: Requirements 4.5, 5.1**

- [x] 8. 出力とロギングの実装
  - [x] 8.1 Logger クラスを実装
    - ログレベル（DEBUG, INFO, WARNING, ERROR）のサポート
    - ファイルと標準エラー出力へのログ記録
    - 変換開始、完了、エラーの詳細ログ
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  
  - [x] 8.2 ロギングのプロパティテストを作成
    - **Property 42: Log file generation**
    - **Property 43: Conversion start logging**
    - **Property 44: Conversion completion logging**
    - **Property 45: Error and warning logging**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4**
  
  - [x] 8.3 OutputWriter クラスを実装
    - ファイルへの書き込み、標準出力への出力、プレビュー表示
    - _Requirements: 6.2, 11.1, 11.2_
  
  - [x] 8.4 出力のプロパティテストを作成
    - **Property 26: Output destination**
    - **Property 46: Preview mode file handling**
    - **Property 47: Preview line limit**
    - **Validates: Requirements 6.2, 11.1, 11.2**

- [x] 9. 設定管理の実装
  - [x] 9.1 ConversionConfig データクラスを実装
    - すべての設定オプションを含むデータクラス
    - デフォルト値の設定
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 9.2 ConfigManager クラスを実装
    - YAML設定ファイルの読み込みと保存
    - CLI引数と設定ファイルのマージ
    - _Requirements: 8.6, 8.7_
  
  - [x] 9.3 設定管理のプロパティテストを作成
    - **Property 39: Configuration file support**
    - **Validates: Requirements 8.6, 8.7**

- [x] 10. Checkpoint - Phase 1 MVP完成
  - すべてのテストが成功することを確認
  - Word文書の完全な変換パイプラインが動作することを確認
  - CLIから実行可能であることを確認
  - 質問があればユーザーに確認

- [x] 11. Excel パーサーの実装
  - [x] 11.1 ExcelParser クラスを実装
    - openpyxl を使用してExcelファイルを読み込む
    - すべてのシートを抽出して内部表現に変換
    - 数式の計算値を取得
    - 結合セルの処理（値を全セルに展開）
    - 数式エラー（#DIV/0!, #VALUE!, #REF!等）の処理
    - ハイパーリンクの抽出とMarkdown形式への変換
    - 日付・時刻のフォーマット処理
    - 非表示行・列の処理（デフォルト：含める）
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  
  - [x] 11.2 Excel変換のプロパティテストを作成
    - **Property 8: Sheet extraction**
    - **Property 9: Multi-sheet handling**
    - **Property 10: Data table conversion**
    - **Property 11: Formula value conversion**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
  
  - [x] 11.3 Excel特殊ケースのエッジケーステストを作成
    - 空のExcelシートの処理を検証
    - 結合セルの処理を検証
    - 数式エラーの処理を検証
    - ハイパーリンクの変換を検証
    - 非表示行・列の処理を検証
    - _Requirements: 2.5_

- [x] 12. PDF パーサーの実装（テキスト抽出のみ）
  - [x] 12.1 PDFParser クラスの基本構造を実装
    - PyPDF2 と pdfplumber を使用してPDFを読み込む
    - テキストコンテンツを抽出
    - _Requirements: 3.1_
  
  - [x] 12.2 PDFテキスト抽出のプロパティテストを作成
    - **Property 12: PDF text extraction**
    - **Validates: Requirements 3.1**
  
  - [x] 12.3 PDF構造検出機能を追加
    - 見出しの検出（フォントサイズと太字から推測）
    - 表の検出と抽出（pdfplumber使用）
    - _Requirements: 3.2, 3.3_
  
  - [x] 12.4 PDF構造検出のプロパティテストを作成
    - **Property 13: PDF heading detection**
    - **Property 14: PDF table preservation**
    - **Validates: Requirements 3.2, 3.3**

- [x] 13. 画像抽出機能の実装
  - [x] 13.1 ImageExtractor クラスを実装
    - ドキュメントから画像を抽出
    - 適切なディレクトリ構造で保存（{filename}/images/）
    - 連番または元のファイル名での保存
    - _Requirements: 7.1, 7.2, 7.3, 7.6_
  
  - [x] 13.2 画像抽出のプロパティテストを作成
    - **Property 28: Image directory creation**
    - **Property 29: Image naming convention**
    - **Property 31: Image format support**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.6**
  
  - [x] 13.3 Markdown内の画像参照を実装
    - 相対パスでの画像参照
    - 抽出失敗時のプレースホルダー
    - _Requirements: 7.4, 7.7_
  
  - [x] 13.4 画像参照のプロパティテストを作成
    - **Property 30: Relative path references**
    - **Property 32: Image extraction failure handling**
    - **Validates: Requirements 7.4, 7.7**

- [x] 14. Checkpoint - Phase 2 完成
  - すべてのテストが成功することを確認
  - Word、Excel、PDFの基本変換が動作することを確認
  - 画像抽出が正しく機能することを確認
  - 質問があればユーザーに確認

- [x] 15. OCR エンジンの統合
  - [x] 15.1 OCREngine クラスを実装
    - pytesseract を使用してOCRを実行
    - 多言語サポート（デフォルト: eng+jpn）
    - 画像バイトまたはファイルパスからのテキスト抽出
    - _Requirements: 3.4, 3.5, 3.7, 7.8_
  
  - [x] 15.2 OCR機能のプロパティテストを作成
    - **Property 15: OCR on PDF images**
    - **Property 16: Scanned PDF OCR**
    - **Property 17: Multi-language OCR support**
    - **Property 33: OCR on images with text**
    - **Validates: Requirements 3.4, 3.5, 3.7, 7.8**
  
  - [x] 15.3 OCRテキストのマーキング機能を実装
    - OCR抽出テキストに適切なマーカーを追加
    - _Requirements: 7.11_
  
  - [x] 15.4 OCRマーキングのプロパティテストを作成
    - **Property 34: OCR text marking**
    - **Validates: Requirements 7.11**
  
  - [x] 15.5 手書きメモOCRのエッジケーステストを作成
    - 手書きメモの認識テスト（ベストエフォート）
    - _Requirements: 3.6, 7.9_
  
  - [x] 15.6 OCR言語設定の統合テストを作成
    - 言語設定オプションのテスト
    - _Requirements: 7.10_

- [x] 16. バッチ変換とプレビュー機能の実装
  - [x] 16.1 バッチ変換機能を実装
    - 複数ファイルの一括変換
    - 各ファイルの変換結果を集約
    - _Requirements: 6.5_
  
  - [x] 16.2 バッチ変換のプロパティテストを作成
    - **Property 27: Batch conversion**
    - **Validates: Requirements 6.5**
  
  - [x] 16.3 Dry-runモードを実装
    - ファイル書き込みなしで変換を実行
    - _Requirements: 11.5_
  
  - [x] 16.4 Dry-runモードのプロパティテストを作成
    - **Property 49: Dry-run mode**
    - **Validates: Requirements 11.5**
  
  - [x] 16.5 進捗インジケーターの統合テストを作成
    - 大きなファイルの変換時の進捗表示テスト
    - _Requirements: 6.3_

- [x] 17. カスタマイズオプションの実装
  - [x] 17.1 見出しレベルオフセット機能を実装
    - 設定に基づいて見出しレベルを調整
    - _Requirements: 8.1_
  
  - [x] 17.2 見出しオフセットのプロパティテストを作成
    - **Property 35: Heading level offset**
    - **Validates: Requirements 8.1**
  
  - [x] 17.3 メタデータ制御機能を実装
    - メタデータの包含/除外オプション
    - _Requirements: 8.3_
  
  - [x] 17.4 メタデータ制御のプロパティテストを作成
    - **Property 36: Metadata inclusion control**
    - **Validates: Requirements 8.3**
  
  - [x] 17.5 画像処理モード選択を実装
    - ファイル抽出 vs Base64埋め込み
    - _Requirements: 8.4_
  
  - [x] 17.6 画像処理モードのプロパティテストを作成
    - **Property 37: Image handling mode**
    - **Validates: Requirements 8.4**
  
  - [x] 17.7 表スタイル選択の統合テストを作成
    - 異なる表フォーマットスタイルのテスト
    - _Requirements: 8.2_

- [x] 18. 文字エンコーディング処理の実装
  - [x] 18.1 エンコーディング検出機能を実装
    - 入力ファイルのエンコーディング自動検出
    - _Requirements: 9.1_
  
  - [x] 18.2 エンコーディング検出のプロパティテストを作成
    - **Property 40: Multi-encoding detection**
    - **Validates: Requirements 9.1**
  
  - [x] 18.3 UTF-8出力の確保
    - デフォルトでUTF-8エンコーディングで出力
    - _Requirements: 8.5, 9.2_
  
  - [x] 18.4 UTF-8出力のプロパティテストを作成
    - **Property 38: UTF-8 encoding output**
    - **Validates: Requirements 8.5, 9.2**
  
  - [x] 18.5 エンコーディング問題のロギング
    - エンコーディング問題検出時の警告ログ
    - _Requirements: 9.5_
  
  - [x] 18.6 エンコーディングロギングのプロパティテストを作成
    - **Property 41: Encoding issue logging**
    - **Validates: Requirements 9.5**
  
  - [x] 18.7 エンコーディングオプションの統合テストを作成
    - 出力エンコーディング選択のテスト
    - _Requirements: 9.4_

- [x] 19. 検証機能の実装
  - [x] 19.1 Markdown検証モードを実装
    - markdown-it-py を使用して構文検証
    - _Requirements: 11.3, 11.4_
  
  - [x] 19.2 検証機能のプロパティテストを作成
    - **Property 48: Validation error reporting**
    - **Validates: Requirements 11.4**
  
  - [x] 19.3 検証モードの統合テストを作成
    - 検証モードの動作テスト
    - _Requirements: 11.3_

- [x] 20. ラウンドトリップ検証の実装
  - [x] 20.1 ラウンドトリッププロパティテストを作成
    - **Property 53: Round-trip semantic equivalence**
    - **Validates: Requirements 12.4**
    - ソースドキュメント → 内部表現 → Markdown → 解析 の一貫性を検証

- [x] 21. DiagramConverter の基本実装（限定的）
  - [x] 21.1 DiagramConverter クラスの基本構造を実装
    - シンプルな図の検出（ベストエフォート）
    - 基本的なMermaid構文への変換（限定的な機能）
    - _Requirements: 7.5_
  
  - [ ] 21.2 図変換の統合テストを作成
    - 図のMermaid変換テスト（ベストエフォート）
    - _Requirements: 7.5_

- [x] 22. Checkpoint - Phase 3 完成
  - すべてのテストが成功することを確認
  - OCR、バッチ変換、カスタマイズオプションが動作することを確認
  - 設定ファイルからの読み込みが正しく機能することを確認
  - 質問があればユーザーに確認

- [x] 23. エラーハンドリングの強化
  - [x] 23.1 空ファイルのエッジケーステストを作成
    - 空ファイルの処理テスト
    - _Requirements: 4.3_
  
  - [x] 23.2 包括的なエラーハンドリングの統合テストを作成
    - すべてのエラーカテゴリのテスト
    - エラーメッセージの品質検証
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 24. ドキュメントとREADMEの作成
  - README.md を作成（インストール、使用方法、例）
  - CLI ヘルプメッセージを充実させる
  - 設定ファイルのサンプルを作成
  - _Requirements: 6.1_

- [x] 25. 最終統合テストとエンドツーエンドテスト
  - [x] 25.1 エンドツーエンド統合テストを作成
    - 実際のサンプルファイルを使用した完全な変換フローのテスト
    - Word、Excel、PDFそれぞれの実例テスト
    - すべての主要機能の統合テスト

- [x] 26. Final Checkpoint - 全機能完成
  - すべてのテストが成功することを確認
  - すべての要件が実装されていることを確認
  - パフォーマンスが許容範囲内であることを確認
  - ドキュメントが完全であることを確認
  - 質問があればユーザーに確認

- [x] 27. 実ファイルによるユースケース検証（初期テスト - docs_target/tps65053.pdf）
  - [x] 27.1 docs_target/tps65053.pdf を使用した基本変換テスト
    - PDFからMarkdownへの変換を実行
    - テキスト抽出の品質を確認
    - 表の検出と変換を検証
    - 見出し構造の検出を確認
    - 出力されたMarkdownの可読性を評価
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 28. 包括的ユースケース検証（docs_target2 PDFファイル群）
  - [x] 28.1 docs_target2/tps653850-q1.pdf の完全変換テスト
    - PDFからMarkdownへの完全変換を実行
    - テキスト抽出の品質を確認
    - 表の検出と変換を検証
    - 見出し構造の検出を確認
    - 画像抽出を実行し、適切なディレクトリに保存されることを確認
    - 抽出された画像のMarkdown参照が正しいことを確認
    - OCR機能を有効にして画像内テキストを抽出
    - OCRマーキングが適切に付与されているか確認
    - 出力されたMarkdownの可読性を評価
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.2, 7.3, 7.4, 7.11_
  
  - [x] 28.2 docs_target2/tcan1463-q1.pdf の完全変換テスト
    - PDFからMarkdownへの完全変換を実行
    - テキスト抽出の品質を確認
    - 表の検出と変換を検証
    - 見出し構造の検出を確認
    - 画像抽出を実行し、適切なディレクトリに保存されることを確認
    - 抽出された画像のMarkdown参照が正しいことを確認
    - OCR機能を有効にして画像内テキストを抽出
    - OCRマーキングが適切に付与されているか確認
    - 出力されたMarkdownの可読性を評価
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.2, 7.3, 7.4, 7.11_
  
  - [x] 28.3 docs_target2/infineon-tle9180d-31qk-datasheet-en.pdf の完全変換テスト
    - PDFからMarkdownへの完全変換を実行
    - テキスト抽出の品質を確認
    - 表の検出と変換を検証
    - 見出し構造の検出を確認
    - 画像抽出を実行し、適切なディレクトリに保存されることを確認
    - 抽出された画像のMarkdown参照が正しいことを確認
    - OCR機能を有効にして画像内テキストを抽出
    - OCRマーキングが適切に付与されているか確認
    - 出力されたMarkdownの可読性を評価
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.2, 7.3, 7.4, 7.11_
  
  - [x] 28.4 変換結果の品質評価とファクトチェック
    - 各PDFの生成されたMarkdownファイルを詳細レビュー
    - 元のPDFと比較して情報の損失がないか確認
    - 技術仕様、数値、表データの正確性を検証
    - フォーマットの適切性を評価
    - 画像抽出の完全性を確認（全ての図表が抽出されているか）
    - OCRテキストの精度を評価
    - 改善点があれば記録
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 7.1, 7.2, 7.3, 7.4, 7.11_

- [x] 29. LLMによる変換品質の自動評価（オプション）
  - [x] 29.1 Ollama統合のセットアップ
    - Ollamaクライアントライブラリをインストール
    - ローカルLLMモデル（例: llama3, mistral）をセットアップ
    - LLM評価スクリプトの基本構造を作成
  
  - [x] 29.2 LLMによる文章校正と品質評価
    - 変換されたMarkdownをLLMに入力
    - 以下の観点で自動評価を実施：
      - 文章の流暢性と可読性
      - 技術用語の一貫性
      - 構造の論理性
      - 情報の完全性（元PDFとの比較）
      - 表データの整合性
    - 評価結果をレポート形式で出力
    - スコアリングシステムの実装（0-100点）
  
  - [x] 29.3 LLMによるファクトチェック
    - 元のPDFから抽出した情報とMarkdownの内容を比較
    - 数値、仕様、技術データの一致を確認
    - 不一致がある場合は詳細レポートを生成
    - 信頼度スコアを算出
  
  - [x] 29.4 自動評価レポートの生成
    - 各PDFファイルの評価結果をまとめたレポートを生成
    - 品質スコア、改善提案、検出された問題点を含む
    - レポートをMarkdown形式で出力（docs/conversion_quality_report.md）

- [ ] 30. LLMによる文章修正・校正機能の実装（オプション）
  - [ ] 30.1 TextProofreader クラスの実装
    - Ollamaを使用してMarkdownテキストを解析
    - 誤字脱字の検出と修正
    - 文法エラーの検出と修正
    - 不自然な改行の修正
    - 孤立文字の統合
    - 技術用語の一貫性チェック
    - 修正前後の差分を生成
    - _Requirements: 新規_
  
  - [ ] 30.2 修正モードの実装
    - 自動修正モード（確認なしで適用）
    - インタラクティブモード（修正案を表示して確認）
    - Dry-runモード（修正案のみ表示）
    - 修正履歴の記録
    - _Requirements: 新規_
  
  - [ ] 30.3 OCR結果の統合修正
    - OCRで抽出されたテキストの品質向上
    - OCRエラーの自動修正（文脈から推測）
    - 技術文書特有の用語の修正
    - 数値・記号の正確性向上
    - _Requirements: 新規_
  
  - [ ] 30.4 CLI統合
    - `--proofread` オプションの追加
    - `--proofread-mode` オプション（auto/interactive/dry-run）
    - `--proofread-model` オプション（使用するLLMモデル指定）
    - 修正結果の保存先指定
    - _Requirements: 新規_
  
  - [ ] 30.5 修正機能のテスト
    - 誤字脱字修正のテスト
    - 文法修正のテスト
    - OCR結果修正のテスト
    - 差分生成のテスト
    - _Requirements: 新規_
  
  - [ ] 30.6 ドキュメント更新
    - README.mdに校正機能の説明を追加
    - 使用例とベストプラクティスを記載
    - 制限事項と注意点を明記
    - _Requirements: 新規_

## Notes

- `*` マークのタスクはオプションで、より速いMVP実装のためにスキップ可能です
- 各タスクは特定の要件を参照しており、トレーサビリティを確保しています
- チェックポイントタスクは段階的な検証を保証します
- プロパティテストは普遍的な正確性プロパティを検証します
- ユニットテストは特定の例とエッジケースを検証します
- Phase 1（タスク1-10）でMVPが完成し、基本的なWord変換が可能になります
- Phase 2（タスク11-14）でExcel、PDF、画像抽出が追加されます
- Phase 3（タスク15-22）でOCR、バッチ処理、高度な機能が追加されます
- Phase 4（タスク23-26）で品質向上と最終調整を行います
- Phase 5（タスク30）でLLMによる文章修正・校正機能が追加されます（オプション）
