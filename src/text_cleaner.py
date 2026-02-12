"""PDFから抽出されたテキストのクリーニングモジュール"""

import re
from typing import List


class TextCleaner:
    """PDFから抽出されたテキストをクリーニングするクラス"""
    
    def __init__(self):
        """初期化"""
        pass
    
    def clean_text(self, text: str) -> str:
        """テキスト全体をクリーニング
        
        Args:
            text: クリーニング対象のテキスト
            
        Returns:
            クリーニング済みのテキスト
        """
        # 1. 孤立した1-2文字の行を削除
        text = self._remove_orphan_lines(text)
        
        # 2. 不適切な改行を修正
        text = self._fix_line_breaks(text)
        
        # 3. 連続する空行を削減
        text = self._reduce_empty_lines(text)
        
        # 4. 行末の空白を削除
        text = self._remove_trailing_spaces(text)
        
        return text
    
    def _remove_orphan_lines(self, text: str) -> str:
        """孤立した1-2文字の行を削除
        
        Args:
            text: 処理対象のテキスト
            
        Returns:
            処理済みのテキスト
        """
        lines = text.split('\n')
        cleaned_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 空行はそのまま保持
            if not stripped:
                cleaned_lines.append(line)
                continue
            
            # 1-2文字の行で、前後が空行または存在しない場合は削除
            if len(stripped) <= 2:
                # 前後の行を確認
                prev_empty = i == 0 or not lines[i-1].strip()
                next_empty = i == len(lines)-1 or not lines[i+1].strip()
                
                # 数字のみの行は保持（ページ番号の可能性）
                if stripped.isdigit():
                    cleaned_lines.append(line)
                # 前後が空行の場合は削除
                elif prev_empty and next_empty:
                    continue
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _fix_line_breaks(self, text: str) -> str:
        """不適切な改行を修正
        
        PDFから抽出されたテキストでは、段落の途中で改行されることがある。
        文末でない改行を検出して結合する。
        
        Args:
            text: 処理対象のテキスト
            
        Returns:
            処理済みのテキスト
        """
        lines = text.split('\n')
        fixed_lines = []
        buffer = []
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 空行は段落の区切りとして扱う
            if not stripped:
                if buffer:
                    fixed_lines.append(' '.join(buffer))
                    buffer = []
                fixed_lines.append('')
                continue
            
            # 見出しっぽい行（短い、大文字、数字で始まる）はそのまま
            if self._is_likely_heading(stripped):
                if buffer:
                    fixed_lines.append(' '.join(buffer))
                    buffer = []
                fixed_lines.append(line)
                continue
            
            # 文末記号で終わる行
            if stripped[-1] in '.!?。！？':
                buffer.append(stripped)
                fixed_lines.append(' '.join(buffer))
                buffer = []
                continue
            
            # 箇条書き記号で始まる行
            if re.match(r'^[•\-\*\+]\s', stripped):
                if buffer:
                    fixed_lines.append(' '.join(buffer))
                    buffer = []
                fixed_lines.append(line)
                continue
            
            # それ以外はバッファに追加
            buffer.append(stripped)
        
        # 残りのバッファを処理
        if buffer:
            fixed_lines.append(' '.join(buffer))
        
        return '\n'.join(fixed_lines)
    
    def _is_likely_heading(self, text: str) -> bool:
        """見出しらしい行かどうかを判定
        
        Args:
            text: 判定対象のテキスト
            
        Returns:
            見出しらしい場合True
        """
        # 短い行（80文字以下）
        if len(text) > 80:
            return False
        
        # 数字で始まる（章番号など）
        if re.match(r'^\d+[\.\)]\s', text):
            return True
        
        # 全て大文字
        if text.isupper() and len(text) > 3:
            return True
        
        # 文末記号がない
        if text[-1] not in '.!?。！？,;:、；：':
            return True
        
        return False
    
    def _reduce_empty_lines(self, text: str) -> str:
        """連続する空行を最大2行に削減
        
        Args:
            text: 処理対象のテキスト
            
        Returns:
            処理済みのテキスト
        """
        # 3行以上の連続する空行を2行に削減
        text = re.sub(r'\n\n\n+', '\n\n', text)
        return text
    
    def _remove_trailing_spaces(self, text: str) -> str:
        """各行の行末空白を削除
        
        Args:
            text: 処理対象のテキスト
            
        Returns:
            処理済みのテキスト
        """
        lines = text.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        return '\n'.join(cleaned_lines)
    
    def clean_paragraph(self, paragraph: str) -> str:
        """段落単位でクリーニング
        
        Args:
            paragraph: クリーニング対象の段落
            
        Returns:
            クリーニング済みの段落
        """
        # 連続する空白を1つに
        paragraph = re.sub(r'\s+', ' ', paragraph)
        
        # 前後の空白を削除
        paragraph = paragraph.strip()
        
        return paragraph
