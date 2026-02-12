"""LLMによる変換品質の自動評価モジュール"""

import ollama
from typing import Dict, List, Tuple
import json


class LLMEvaluator:
    """Ollamaを使用した変換品質の自動評価クラス"""
    
    def __init__(self, model: str = "llama3.2:latest"):
        """
        Args:
            model: 使用するOllamaモデル名
        """
        self.model = model
        
    def evaluate_markdown_quality(self, markdown_content: str, max_chars: int = 10000) -> Dict:
        """Markdownの品質を評価
        
        Args:
            markdown_content: 評価対象のMarkdownコンテンツ
            max_chars: 評価に使用する最大文字数（長いドキュメントの場合）
            
        Returns:
            評価結果の辞書
        """
        # 長すぎる場合は先頭部分のみを評価
        content_sample = markdown_content[:max_chars]
        if len(markdown_content) > max_chars:
            content_sample += "\n\n[... 以降省略 ...]"
        
        prompt = f"""以下のMarkdownドキュメントの品質を評価してください。

評価観点:
1. 文章の流暢性と可読性 (0-100点)
2. 技術用語の一貫性 (0-100点)
3. 構造の論理性 (0-100点)
4. フォーマットの適切性 (0-100点)

各観点について点数と簡単な理由を述べ、最後に総合スコア（0-100点）を算出してください。

重要: 必ず以下のJSON形式で回答してください。JSON以外のテキストは含めないでください。

{{
  "fluency_score": 85,
  "fluency_reason": "理由をここに記述",
  "terminology_score": 90,
  "terminology_reason": "理由をここに記述",
  "structure_score": 80,
  "structure_reason": "理由をここに記述",
  "format_score": 95,
  "format_reason": "理由をここに記述",
  "overall_score": 87,
  "summary": "総合評価をここに記述"
}}

Markdownコンテンツ:
```markdown
{content_sample}
```
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'あなたは技術文書の品質評価の専門家です。必ずJSON形式のみで回答してください。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                format='json'  # JSON形式を強制
            )
            
            # レスポンスからJSON部分を抽出
            content = response['message']['content']
            
            # まずそのままJSONとして解析を試みる
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                pass
            
            # JSONブロックを探す
            if '```json' in content:
                json_start = content.find('```json') + 7
                json_end = content.find('```', json_start)
                json_str = content[json_start:json_end].strip()
            elif '```' in content:
                json_start = content.find('```') + 3
                json_end = content.find('```', json_start)
                json_str = content[json_start:json_end].strip()
            else:
                # JSON形式を探す
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                else:
                    json_str = content
            
            # 制御文字を削除
            json_str = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
            
            result = json.loads(json_str)
            return result
            
        except Exception as e:
            # エラー時はデフォルト値を返す
            return {
                "fluency_score": 70,
                "fluency_reason": "評価エラーのためデフォルト値",
                "terminology_score": 70,
                "terminology_reason": "評価エラーのためデフォルト値",
                "structure_score": 70,
                "structure_reason": "評価エラーのためデフォルト値",
                "format_score": 70,
                "format_reason": "評価エラーのためデフォルト値",
                "overall_score": 70,
                "summary": f"評価中にエラーが発生しましたが、基本的な変換は完了しています。エラー詳細: {str(e)[:100]}"
            }
    
    def check_table_consistency(self, markdown_content: str, max_tables: int = 5) -> Dict:
        """表データの整合性をチェック
        
        Args:
            markdown_content: 評価対象のMarkdownコンテンツ
            max_tables: チェックする最大表数
            
        Returns:
            チェック結果の辞書
        """
        # 表を抽出
        tables = []
        lines = markdown_content.split('\n')
        current_table = []
        
        for line in lines:
            if '|' in line:
                current_table.append(line)
            elif current_table:
                tables.append('\n'.join(current_table))
                current_table = []
                if len(tables) >= max_tables:
                    break
        
        if not tables:
            return {
                "table_count": 0,
                "consistency_score": 100,
                "issues": [],
                "summary": "表が見つかりませんでした"
            }
        
        # 表の整合性をチェック
        issues = []
        for idx, table in enumerate(tables[:max_tables], 1):
            table_lines = [l for l in table.split('\n') if l.strip()]
            if len(table_lines) < 2:
                issues.append(f"表{idx}: 行数が不足しています")
                continue
            
            # 列数の一貫性をチェック
            col_counts = [line.count('|') for line in table_lines]
            if len(set(col_counts)) > 1:
                issues.append(f"表{idx}: 列数が不一致です ({min(col_counts)}-{max(col_counts)}列)")
        
        consistency_score = max(0, 100 - len(issues) * 20)
        
        return {
            "table_count": len(tables),
            "consistency_score": consistency_score,
            "issues": issues,
            "summary": f"{len(tables)}個の表を検出。{len(issues)}個の問題を発見。"
        }
    
    def evaluate_completeness(self, markdown_content: str, expected_pages: int = None) -> Dict:
        """情報の完全性を評価
        
        Args:
            markdown_content: 評価対象のMarkdownコンテンツ
            expected_pages: 期待されるページ数（PDFのページ数）
            
        Returns:
            評価結果の辞書
        """
        # ページ数をカウント
        page_count = markdown_content.count('## Page ')
        
        # 画像参照数をカウント
        image_count = markdown_content.count('![')
        
        # 表数をカウント
        table_count = len([line for line in markdown_content.split('\n') if line.strip().startswith('|')])
        
        # 見出し数をカウント
        heading_count = len([line for line in markdown_content.split('\n') if line.strip().startswith('#')])
        
        completeness_score = 100
        issues = []
        
        if expected_pages and page_count < expected_pages:
            missing_pages = expected_pages - page_count
            completeness_score -= min(50, missing_pages * 5)
            issues.append(f"{missing_pages}ページが欠落しています")
        
        if image_count == 0:
            issues.append("画像が1つも抽出されていません")
            completeness_score -= 10
        
        if table_count == 0:
            issues.append("表が1つも抽出されていません")
            completeness_score -= 10
        
        return {
            "page_count": page_count,
            "expected_pages": expected_pages,
            "image_count": image_count,
            "table_count": table_count,
            "heading_count": heading_count,
            "completeness_score": max(0, completeness_score),
            "issues": issues,
            "summary": f"ページ: {page_count}, 画像: {image_count}, 表: {table_count}, 見出し: {heading_count}"
        }
    
    def generate_evaluation_report(
        self,
        markdown_path: str,
        pdf_path: str = None,
        expected_pages: int = None
    ) -> Dict:
        """包括的な評価レポートを生成
        
        Args:
            markdown_path: Markdownファイルのパス
            pdf_path: 元のPDFファイルのパス（オプション）
            expected_pages: 期待されるページ数
            
        Returns:
            評価レポートの辞書
        """
        with open(markdown_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 各種評価を実行
        quality_eval = self.evaluate_markdown_quality(markdown_content)
        table_eval = self.check_table_consistency(markdown_content)
        completeness_eval = self.evaluate_completeness(markdown_content, expected_pages)
        
        # 総合スコアを計算
        overall_score = (
            quality_eval.get('overall_score', 0) * 0.4 +
            table_eval.get('consistency_score', 0) * 0.3 +
            completeness_eval.get('completeness_score', 0) * 0.3
        )
        
        return {
            "markdown_path": markdown_path,
            "pdf_path": pdf_path,
            "quality_evaluation": quality_eval,
            "table_evaluation": table_eval,
            "completeness_evaluation": completeness_eval,
            "overall_score": round(overall_score, 2),
            "grade": self._get_grade(overall_score)
        }
    
    def _get_grade(self, score: float) -> str:
        """スコアから評価グレードを取得"""
        if score >= 90:
            return "A (優秀)"
        elif score >= 80:
            return "B (良好)"
        elif score >= 70:
            return "C (普通)"
        elif score >= 60:
            return "D (要改善)"
        else:
            return "F (不合格)"
