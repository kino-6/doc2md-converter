"""OCR結果の統合修正モジュール

このモジュールは、OCRで抽出されたテキストの品質を向上させます。
OCR特有のエラーを自動修正し、技術文書の精度を高めます。
"""

from typing import Dict, List, Optional, Tuple
import re

from src.text_proofreader import TextProofreader, ProofreadingResult


class OCRProofreader:
    """OCR結果を修正するクラス
    
    OCRで抽出されたテキストに対して以下の処理を行います:
    - OCR特有のエラーの自動修正
    - 技術文書特有の用語の修正
    - 数値・記号の正確性向上
    - 文脈からの推測による修正
    """
    
    # OCR特有の誤認識パターン
    OCR_ERROR_PATTERNS = {
        # 文字の混同
        r'\bl\b': 'I',  # 小文字エル → 大文字アイ（文脈依存）
        r'\bO\b': '0',  # 大文字オー → ゼロ（数値文脈）
        r'rn': 'm',     # rn → m
        r'vv': 'w',     # vv → w
        r'\|': 'l',     # パイプ → 小文字エル（文脈依存）
        
        # スペースの問題
        r'(\w)([A-Z])': r'\1 \2',  # 単語間のスペース欠落
        r'\s{2,}': ' ',  # 過剰なスペース
        
        # 句読点
        r'\.{2,}': '.',  # 重複したピリオド
        r',{2,}': ',',   # 重複したカンマ
    }
    
    # 技術用語の一般的な誤認識
    TECHNICAL_TERM_CORRECTIONS = {
        'APl': 'API',
        'l/O': 'I/O',
        'CPu': 'CPU',
        'RAm': 'RAM',
        'RoM': 'ROM',
        'USb': 'USB',
        'HDMl': 'HDMI',
        'GPu': 'GPU',
        'SQLite': 'SQLite',
        'MySqL': 'MySQL',
        'PostgreSqL': 'PostgreSQL',
    }
    
    def __init__(self, proofreader: Optional[TextProofreader] = None):
        """
        Args:
            proofreader: TextProofreaderインスタンス（LLMベースの修正用）
        """
        self.proofreader = proofreader or TextProofreader()
    
    def correct_ocr_text(
        self,
        text: str,
        is_technical: bool = True,
        use_llm: bool = True
    ) -> ProofreadingResult:
        """OCRテキストを修正
        
        Args:
            text: OCR抽出されたテキスト
            is_technical: 技術文書かどうか
            use_llm: LLMベースの修正を使用するか
        
        Returns:
            ProofreadingResult: 修正結果
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
        
        # ステップ1: ルールベースの修正
        rule_based_result = self._apply_rule_based_corrections(text, is_technical)
        
        # ステップ2: LLMベースの修正（オプション）
        if use_llm:
            llm_result = self.proofreader.proofread_ocr_text(
                rule_based_result['corrected_text'],
                is_technical=is_technical
            )
            
            # 両方の変更をマージ
            all_changes = rule_based_result['changes'] + llm_result.changes
            
            return ProofreadingResult(
                original_text=text,
                corrected_text=llm_result.corrected_text,
                changes=all_changes,
                issues_found=len(all_changes),
                corrections_applied=len(all_changes),
                diff=self.proofreader._generate_diff(text, llm_result.corrected_text)
            )
        else:
            # ルールベースのみ
            return ProofreadingResult(
                original_text=text,
                corrected_text=rule_based_result['corrected_text'],
                changes=rule_based_result['changes'],
                issues_found=len(rule_based_result['changes']),
                corrections_applied=len(rule_based_result['changes']),
                diff=self.proofreader._generate_diff(text, rule_based_result['corrected_text'])
            )
    
    def correct_numbers_and_symbols(self, text: str) -> Tuple[str, List[Dict]]:
        """数値と記号の修正
        
        Args:
            text: 修正対象のテキスト
        
        Returns:
            (修正後のテキスト, 変更リスト)
        """
        corrected = text
        changes = []
        
        # 数値内のスペースを削除（例: "1 234" → "1234"）
        pattern = r'(\d)\s+(\d)'
        matches = re.finditer(pattern, corrected)
        for match in matches:
            original = match.group(0)
            replacement = match.group(1) + match.group(2)
            corrected = corrected.replace(original, replacement, 1)
            changes.append({
                'type': 'number_spacing',
                'original': original,
                'corrected': replacement,
                'reason': '数値内の不要なスペースを削除'
            })
        
        # 小数点の修正（例: "3,14" → "3.14"）
        pattern = r'(\d),(\d)'
        matches = re.finditer(pattern, corrected)
        for match in matches:
            original = match.group(0)
            replacement = match.group(1) + '.' + match.group(2)
            corrected = corrected.replace(original, replacement, 1)
            changes.append({
                'type': 'decimal_point',
                'original': original,
                'corrected': replacement,
                'reason': '小数点の修正'
            })
        
        # 単位の修正（スペースの正規化）
        units = ['MHz', 'GHz', 'KB', 'MB', 'GB', 'TB', 'V', 'A', 'W', 'Ω', '°C', '°F']
        for unit in units:
            # 数値と単位の間にスペースがない場合
            pattern = rf'(\d)({re.escape(unit)})'
            matches = re.finditer(pattern, corrected)
            for match in matches:
                original = match.group(0)
                replacement = match.group(1) + ' ' + match.group(2)
                corrected = corrected.replace(original, replacement, 1)
                changes.append({
                    'type': 'unit_spacing',
                    'original': original,
                    'corrected': replacement,
                    'reason': '数値と単位の間にスペースを追加'
                })
        
        return corrected, changes
    
    def correct_technical_terms(self, text: str) -> Tuple[str, List[Dict]]:
        """技術用語の修正
        
        Args:
            text: 修正対象のテキスト
        
        Returns:
            (修正後のテキスト, 変更リスト)
        """
        corrected = text
        changes = []
        
        for wrong, correct in self.TECHNICAL_TERM_CORRECTIONS.items():
            if wrong in corrected:
                corrected = corrected.replace(wrong, correct)
                changes.append({
                    'type': 'technical_term',
                    'original': wrong,
                    'corrected': correct,
                    'reason': f'技術用語の修正: {wrong} → {correct}'
                })
        
        return corrected, changes
    
    def _apply_rule_based_corrections(
        self,
        text: str,
        is_technical: bool
    ) -> Dict:
        """ルールベースの修正を適用
        
        Args:
            text: 修正対象のテキスト
            is_technical: 技術文書かどうか
        
        Returns:
            修正結果の辞書
        """
        corrected = text
        all_changes = []
        
        # 技術用語の修正
        if is_technical:
            corrected, changes = self.correct_technical_terms(corrected)
            all_changes.extend(changes)
        
        # 数値と記号の修正
        corrected, changes = self.correct_numbers_and_symbols(corrected)
        all_changes.extend(changes)
        
        # OCR特有のパターン修正
        for pattern, replacement in self.OCR_ERROR_PATTERNS.items():
            matches = list(re.finditer(pattern, corrected))
            for match in matches:
                original = match.group(0)
                # 文脈を考慮した置換（簡易版）
                if self._should_replace(original, replacement, corrected, match.start()):
                    corrected = corrected[:match.start()] + replacement + corrected[match.end():]
                    all_changes.append({
                        'type': 'ocr_pattern',
                        'original': original,
                        'corrected': replacement,
                        'reason': f'OCRパターン修正: {pattern}'
                    })
        
        return {
            'corrected_text': corrected,
            'changes': all_changes
        }
    
    def _should_replace(
        self,
        original: str,
        replacement: str,
        text: str,
        position: int
    ) -> bool:
        """置換すべきかどうかを判定
        
        文脈を考慮して、置換が適切かどうかを判定します。
        
        Args:
            original: 元の文字列
            replacement: 置換後の文字列
            text: 全体のテキスト
            position: 位置
        
        Returns:
            置換すべきかどうか
        """
        # 簡易的な文脈判定
        # 前後の文字を確認
        context_before = text[max(0, position-10):position]
        context_after = text[position+len(original):min(len(text), position+len(original)+10)]
        
        # 数値文脈での O → 0 変換
        if original == 'O' and replacement == '0':
            # 前後に数字があれば変換
            if re.search(r'\d', context_before) or re.search(r'\d', context_after):
                return True
            return False
        
        # その他のパターンは基本的に変換
        return True
    
    def enhance_ocr_quality(
        self,
        text: str,
        confidence_threshold: float = 0.7
    ) -> ProofreadingResult:
        """OCR品質を総合的に向上
        
        すべての修正手法を組み合わせて、OCRテキストの品質を最大限に向上させます。
        
        Args:
            text: OCR抽出されたテキスト
            confidence_threshold: 信頼度の閾値（未使用、将来の拡張用）
        
        Returns:
            ProofreadingResult: 修正結果
        """
        return self.correct_ocr_text(text, is_technical=True, use_llm=True)
