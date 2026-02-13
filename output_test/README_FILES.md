# output_test ディレクトリのファイル説明

## 最新のフル機能テスト結果

### ✅ tps653850-q1_final_test.md
**最新のフル機能（--full）で生成されたファイル**

- コマンド: `doc2md -i docs_target2/tps653850-q1.pdf -o output_test/tps653850-q1_final_test.md --full`
- 機能:
  - ✅ 画像抽出: 11枚
  - ✅ 文章校正: 3件の修正適用
  - ⚠️ 図→Mermaid変換: 有効化されたが処理時間の問題でスキップ
- 処理時間: 約19分（変換2.42秒 + 校正18分54秒）
- 生成日時: 2026-02-13 12:00-12:19

### 画像ディレクトリ
- `tps653850-q1/images/`: 抽出された11枚の画像

## その他のテストファイル（参考）

### tps653850-q1_diagram_test.md
- テスト: 画像抽出 + 図変換のみ
- サイズ: 14,952 bytes

### tps653850-q1_full_test.md
- テスト: 初期のフル機能テスト（途中で中断）
- サイズ: 7,737 bytes

### tps653850-q1_proofread.md
- テスト: 以前の校正テスト
- サイズ: 10,942 bytes

## 過去のテストファイル

### proofreading_final_usecase_test.md
- Task 30実装時のユースケーステスト結果
- 3つのPDFファイルのテスト結果をまとめたレポート

### infineon-tle9180d-31qk_proofread.md
- 大規模PDF（212ページ）の校正テスト

## 推奨事項

**本番使用時の推奨コマンド:**
```bash
# 画像抽出 + 文章校正（図変換は除外）
doc2md -i document.pdf -o output.md --extract-images --proofread

# または短縮形
doc2md -i document.pdf -o output.md --full
# ただし、図変換は処理時間が長いため、必要に応じて個別に実行
```

**処理時間の目安:**
- 基本変換: 2-3秒（13ページPDF）
- 画像抽出: +0.5秒
- 文章校正: +2-20分（ページ数とテキスト量に依存）
- 図→Mermaid変換: +5-15秒/画像（現在は処理時間が長いため非推奨）
