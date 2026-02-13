"""LLMによる文章修正・校正モジュール

このモジュールは、Ollamaを使用してMarkdownテキストを解析し、
誤字脱字、文法エラー、不自然な改行などを検出・修正します。
"""

import ollama
from typing import Dict, List, Tuple, Optional
import json
import difflib
from dataclasses import dataclass
from tqdm import tqdm


@dataclass
class ProofreadingResult:
    """校正結果を格納するデータクラス"""
    original_text: str
    corrected_text: str
    changes: List[Dict]
    issues_found: int
    corrections_applied: int
    diff: str
    
    def has_changes(self) -> bool:
        """変更があるかどうかを返す"""
        return self.corrections_applied > 0


class TextProofreader:
    """Ollamaを使用したMarkdownテキストの校正クラス
    
    このクラスは以下の機能を提供します:
    - 誤字脱字の検出と修正
    - 文法エラーの検出と修正
    - 不自然な改行の修正
    - 孤立文字の統合
    - 技術用語の一貫性チェック
    - 修正前後の差分生成
    """
    
    def __init__(self, model: str = "llama3.2:latest"):
        """
        Args:
            model: 使用するOllamaモデル名
        """
        self.model = model
    
    def proofread(
        self,
        text: str,
        max_chunk_size: int = 5000,
        focus_areas: Optional[List[str]] = None,
        show_progress: bool = True
    ) -> ProofreadingResult:
        """テキストを校正する
        
        Args:
            text: 校正対象のテキスト
            max_chunk_size: 一度に処理する最大文字数
            focus_areas: 重点的にチェックする領域のリスト
                        (例: ["typos", "grammar", "line_breaks", "terminology"])
            show_progress: 進捗バーを表示するか
        
        Returns:
            ProofreadingResult: 校正結果
        """
        if not text or not text.strip():
            return ProofreadingResult(
                original_text=text,
                corrected_text=text,
                changes=[],
                issues_found=0,
                corrections_applied=0,
                diff=""
            )
        
        # デフォルトの重点領域
        if focus_areas is None:
            focus_areas = ["typos", "grammar", "line_breaks", "isolated_chars", "terminology"]
        
        # テキストをチャンクに分割
        chunks = self._split_into_chunks(text, max_chunk_size)
        
        # 各チャンクを校正
        corrected_chunks = []
        all_changes = []
        
        # 進捗バーの設定
        chunk_iterator = tqdm(chunks, desc="校正処理中", unit="チャンク", disable=not show_progress) if show_progress else chunks
        
        for chunk in chunk_iterator:
            result = self._proofread_chunk(chunk, focus_areas)
            corrected_chunks.append(result['corrected_text'])
            all_changes.extend(result.get('changes', []))
        
        # 結果を結合
        corrected_text = ''.join(corrected_chunks)
        
        # 差分を生成
        diff = self._generate_diff(text, corrected_text)
        
        return ProofreadingResult(
            original_text=text,
            corrected_text=corrected_text,
            changes=all_changes,
            issues_found=len(all_changes),
            corrections_applied=len([c for c in all_changes if c.get('applied', True)]),
            diff=diff
        )
        
        # 差分を生成
        diff = self._generate_diff(text, corrected_text)
        
        return ProofreadingResult(
            original_text=text,
            corrected_text=corrected_text,
            changes=all_changes,
            issues_found=len(all_changes),
            corrections_applied=len([c for c in all_changes if c.get('applied', True)]),
            diff=diff
        )
    
    def proofread_ocr_text(
        self,
        text: str,
        is_technical: bool = True
    ) -> ProofreadingResult:
        """OCR抽出テキストを校正する
        
        OCRテキストに特化した校正を行います:
        - OCR特有のエラー（l/I, 0/O, rn/m など）の修正
        - 技術文書特有の用語の修正
        - 数値・記号の正確性向上
        
        Args:
            text: OCR抽出されたテキスト
            is_technical: 技術文書かどうか
        
        Returns:
            ProofreadingResult: 校正結果
        """
        focus_areas = ["ocr_errors", "technical_terms", "numbers", "symbols"]
        
        if not text or not text.strip():
            return ProofreadingResult(
                original_text=text,
                corrected_text=text,
                changes=[],
                issues_found=0,
                corrections_applied=0,
                diff=""
            )
        
        prompt = self._create_ocr_proofread_prompt(text, is_technical)
        
        try:
            result = self._call_llm(prompt)
            corrected_text = result.get('corrected_text', text)
            changes = result.get('changes', [])
            
            diff = self._generate_diff(text, corrected_text)
            
            return ProofreadingResult(
                original_text=text,
                corrected_text=corrected_text,
                changes=changes,
                issues_found=len(changes),
                corrections_applied=len(changes),
                diff=diff
            )
        except Exception as e:
            # エラー時は元のテキストを返す
            return ProofreadingResult(
                original_text=text,
                corrected_text=text,
                changes=[{"error": str(e)}],
                issues_found=0,
                corrections_applied=0,
                diff=""
            )
    
    def check_terminology_consistency(
        self,
        text: str,
        known_terms: Optional[List[str]] = None
    ) -> Dict:
        """技術用語の一貫性をチェック
        
        Args:
            text: チェック対象のテキスト
            known_terms: 既知の技術用語リスト
        
        Returns:
            Dict: チェック結果
        """
        prompt = f"""以下のテキストから技術用語を抽出し、一貫性をチェックしてください。

同じ概念を指す用語が複数の表記で使われている場合は指摘してください。
例: "データベース" と "DB"、"サーバー" と "サーバ"

必ず以下のJSON形式で回答してください:
{{
  "terms_found": ["用語1", "用語2"],
  "inconsistencies": [
    {{
      "term": "データベース",
      "variants": ["データベース", "DB", "database"],
      "recommendation": "統一すべき表記"
    }}
  ],
  "consistency_score": 85
}}

テキスト:
{text[:3000]}
"""
        
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        'role': 'system',
                        'content': '技術文書の用語一貫性をチェックする専門家です。JSON形式で回答してください。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                format='json'
            )
            
            content = response['message']['content']
            result = self._parse_json_response(content)
            return result
            
        except Exception as e:
            return {
                "terms_found": [],
                "inconsistencies": [],
                "consistency_score": 100,
                "error": str(e)
            }
    
    def _split_into_chunks(self, text: str, max_size: int) -> List[str]:
        """テキストをチャンクに分割
        
        段落や文の境界で分割することを優先します。
        """
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # 段落で分割
        paragraphs = text.split('\n\n')
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_size:
                if current_chunk:
                    current_chunk += '\n\n' + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                
                # 段落が大きすぎる場合は文で分割
                if len(para) > max_size:
                    sentences = para.split('. ')
                    temp_chunk = ""
                    for sent in sentences:
                        if len(temp_chunk) + len(sent) + 2 <= max_size:
                            if temp_chunk:
                                temp_chunk += '. ' + sent
                            else:
                                temp_chunk = sent
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = sent
                    if temp_chunk:
                        current_chunk = temp_chunk
                else:
                    current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _proofread_chunk(self, chunk: str, focus_areas: List[str]) -> Dict:
        """チャンクを校正"""
        prompt = self._create_proofread_prompt(chunk, focus_areas)
        
        try:
            result = self._call_llm(prompt)
            return result
        except Exception as e:
            # エラー時は元のテキストを返す
            return {
                'corrected_text': chunk,
                'changes': [{"error": str(e)}]
            }
    
    def _create_proofread_prompt(self, text: str, focus_areas: List[str]) -> str:
        """校正用のプロンプトを作成"""
        focus_desc = {
            "typos": "誤字脱字",
            "grammar": "文法エラー",
            "line_breaks": "不自然な改行",
            "isolated_chars": "孤立文字",
            "terminology": "技術用語の一貫性"
        }
        
        focus_list = [focus_desc.get(area, area) for area in focus_areas]
        
        return f"""以下のMarkdownテキストを校正してください。

重点チェック項目: {', '.join(focus_list)}

修正ルール:
1. 誤字脱字を修正
2. 文法エラーを修正
3. 不自然な改行を修正（文の途中で改行されている場合）
4. 孤立した文字を前後の文と統合
5. 技術用語の表記を統一
6. Markdown構文は保持
7. 元の意味を変えない

必ず以下のJSON形式で回答してください:
{{
  "corrected_text": "修正後のテキスト全文",
  "changes": [
    {{
      "type": "typo/grammar/line_break/isolated_char/terminology",
      "original": "修正前のテキスト",
      "corrected": "修正後のテキスト",
      "reason": "修正理由"
    }}
  ]
}}

テキスト:
{text}
"""
    
    def _create_ocr_proofread_prompt(self, text: str, is_technical: bool) -> str:
        """OCR校正用のプロンプトを作成"""
        tech_note = "これは技術文書です。技術用語、数値、記号に特に注意してください。" if is_technical else ""
        
        return f"""以下はOCRで抽出されたテキストです。OCR特有のエラーを修正してください。

{tech_note}

OCR特有のエラー例:
- l（小文字エル）と I（大文字アイ）と 1（数字）の混同
- 0（ゼロ）と O（オー）の混同
- rn が m に見える
- 句読点の欠落や誤認識
- スペースの欠落や過剰

必ず以下のJSON形式で回答してください:
{{
  "corrected_text": "修正後のテキスト全文",
  "changes": [
    {{
      "type": "ocr_error",
      "original": "修正前",
      "corrected": "修正後",
      "reason": "修正理由"
    }}
  ]
}}

テキスト:
{text}
"""
    
    def _call_llm(self, prompt: str) -> Dict:
        """LLMを呼び出して結果を取得"""
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    'role': 'system',
                    'content': 'あなたは文章校正の専門家です。JSON形式で回答してください。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            format='json'
        )
        
        content = response['message']['content']
        return self._parse_json_response(content)
    
    def _parse_json_response(self, content: str) -> Dict:
        """JSON レスポンスをパース"""
        # まずそのままJSONとして解析を試みる
        try:
            return json.loads(content)
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
                raise ValueError("JSON形式が見つかりません")
        
        # 制御文字を削除
        json_str = ''.join(char for char in json_str if ord(char) >= 32 or char in '\n\r\t')
        
        return json.loads(json_str)
    
    def _generate_diff(self, original: str, corrected: str) -> str:
        """差分を生成"""
        if original == corrected:
            return "変更なし"
        
        diff_lines = list(difflib.unified_diff(
            original.splitlines(keepends=True),
            corrected.splitlines(keepends=True),
            fromfile='original',
            tofile='corrected',
            lineterm=''
        ))
        
        return ''.join(diff_lines) if diff_lines else "変更なし"
